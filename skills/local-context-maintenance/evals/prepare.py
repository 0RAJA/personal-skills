"""Validate portable cases or prepare one isolated run; never start an agent."""
import argparse
import json
from pathlib import Path, PurePosixPath
import shutil


def safe_path(root, name):
    """Resolve a package-relative path without traversal or symlinks."""
    if not isinstance(name, str) or not name:
        raise ValueError("Relative paths must be nonempty strings")
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or '\\' in name:
        raise ValueError(f'Unsafe relative path: {name}')
    path = root.joinpath(*relative.parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes the input root: {name}")
    if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
        raise ValueError(f'Symlink input is not supported: {name}')
    return path


def load_cases(skill):
    """Check task definitions and exact fixture manifests before any writes."""
    data = json.loads((skill / 'evals/evals.json').read_text(encoding='utf-8'))
    if data.get('skill_name') != 'local-context-maintenance':
        raise ValueError('Unexpected skill_name')
    seen = set()
    for case in data['evals']:
        if type(case['id']) is not int or case['id'] in seen:
            raise ValueError('Case IDs must be unique integers')
        seen.add(case['id'])
        for key in ['name', 'prompt', 'expected_output', 'cold_prompt']:
            if not isinstance(case[key], str) or not case[key].strip():
                raise ValueError(f'Empty field: {key}')
        if not case['expectations'] or not all(isinstance(x, str) and x for x in case['expectations']):
            raise ValueError('Expectations must be nonempty strings')
        fixture = safe_path(skill, case['fixture_root'])
        if not fixture.is_dir() or len(case['files']) != len(set(case['files'])):
            raise ValueError('Invalid fixture root or duplicate files')
        expected = set()
        for name in case['files']:
            path = safe_path(skill, name)
            if not path.is_file() or not path.is_relative_to(fixture):
                raise ValueError(f'Invalid fixture file: {name}')
            expected.add(path)
        actual = set()
        for path in fixture.rglob('*'):
            if path.is_symlink():
                raise ValueError('Fixture symlinks are not supported')
            if path.is_file():
                actual.add(path)
        if expected != actual:
            raise ValueError('Fixture manifest is incomplete')
        for turn in case.get('followups', []):
            if not turn.get('prompt'):
                raise ValueError('Followups need a prompt')
            if 'writable_paths' in turn:
                if not isinstance(turn['writable_paths'], list):
                    raise ValueError('writable_paths must be a list')
                for name in turn['writable_paths']:
                    safe_path(fixture, name)
    return data['evals']


def prepare(skill, case, output):
    """Copy inputs and runtime skill; keep future prompts runner-only."""
    if output.exists() or output.is_relative_to(skill):
        raise ValueError('Output must be a new directory outside the skill package')
    runtime = []
    for name in ['SKILL.md', 'references', 'assets', 'agents', 'scripts']:
        path = skill / name
        if not path.exists():
            continue
        if path.is_symlink() or any(p.is_symlink() for p in path.rglob('*')):
            raise ValueError('Runtime skill symlinks are not supported')
        runtime.append(path)
    output.mkdir(parents=True, exist_ok=False)
    workspace = output / 'workspace'
    workspace.mkdir()
    fixture = safe_path(skill, case['fixture_root'])
    for name in case['files']:
        source = safe_path(skill, name)
        target = workspace / source.relative_to(fixture)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    runtime_root = output / 'runtime-skill'
    runtime_root.mkdir()
    for source in runtime:
        target = runtime_root / source.name
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copyfile(source, target)
    dispatch = {'id': case['id'], 'workspace': str(workspace),
                'skill_path': str(runtime_root / 'SKILL.md'),
                'turns': [{'prompt': case['prompt']}] + case.get('followups', []),
                'cold_prompt': case['cold_prompt']}
    (output / 'dispatch.json').write_text(json.dumps(dispatch, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return dispatch


def main():
    """Offer validation and preparation, without model or service dependencies."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--case', type=int)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    skill = Path(__file__).resolve().parents[1]
    try:
        cases = load_cases(skill)
        if args.check and args.case is None and args.out is None:
            print(json.dumps({'cases': len(cases), 'fixture_files': sum(len(c['files']) for c in cases)}))
            return
        case = next((c for c in cases if c['id'] == args.case), None)
        if args.check or case is None or args.out is None:
            raise ValueError('Use --check, or --case ID --out NEW_DIRECTORY')
        result = prepare(skill, case, args.out.resolve())
        print(json.dumps({'id': result['id'], 'workspace': result['workspace'], 'skill_path': result['skill_path']}))
    except (KeyError, ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
