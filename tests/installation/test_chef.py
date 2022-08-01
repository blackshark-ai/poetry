from packaging.tags import Tag

from poetry.core.packages.utils.link import Link
from poetry.installation.chef import Chef
from poetry.utils._compat import Path
from poetry.utils.env import MockEnv
from poetry.utils.helpers import get_file_hash


def test_get_cached_archive_for_link(config, mocker):
    chef = Chef(
        config,
        MockEnv(
            version_info=(3, 8, 3),
            marker_env={"interpreter_name": "cpython", "interpreter_version": "3.8.3"},
            supported_tags=[
                Tag("cp38", "cp38", "macosx_10_15_x86_64"),
                Tag("py3", "none", "any"),
            ],
        ),
    )

    mocker.patch.object(
        chef,
        "get_cached_archives_for_link",
        return_value=[
            Link("file:///foo/demo-0.1.0-py2.py3-none-any"),
            Link("file:///foo/demo-0.1.0.tar.gz"),
            Link("file:///foo/demo-0.1.0-cp38-cp38-macosx_10_15_x86_64.whl"),
            Link("file:///foo/demo-0.1.0-cp37-cp37-macosx_10_15_x86_64.whl"),
        ],
    )

    archive = chef.get_cached_archive_for_link(
        Link("https://files.python-poetry.org/demo-0.1.0.tar.gz")
    )

    assert Link("file:///foo/demo-0.1.0-cp38-cp38-macosx_10_15_x86_64.whl") == archive


def test_get_cached_archives_for_link(config, mocker):
    chef = Chef(
        config,
        MockEnv(
            marker_env={"interpreter_name": "cpython", "interpreter_version": "3.8.3"}
        ),
    )

    distributions = Path(__file__).parent.parent.joinpath("fixtures/distributions")
    mocker.patch.object(
        chef,
        "get_cache_directory_for_link",
        return_value=distributions,
    )

    demo_file = "demo-0.1.0.tar.gz"
    demo_file_hash_name = "md5"
    demo_file_hash = get_file_hash(distributions / demo_file, demo_file_hash_name)

    no_hash_link = f"https://files.python-poetry.org/{demo_file}"
    cached_archives_for_no_hash_link = {  # all packages
        Link(path.as_uri()) for path in distributions.glob("demo-0.1.0*")
    }

    # link with correct hash
    correct_link = f"{no_hash_link}#{demo_file_hash_name}={demo_file_hash}"
    cached_archives_for_correct_link = {  # only one file with target hash
        Link((distributions / demo_file).as_uri()),
    }

    # link with incorrect hash
    incorrect_link = f"{no_hash_link}#{demo_file_hash_name}={'0' * 32}"
    cached_archives_for_incorrect_link = set()  # no files

    for url, answer in [
        (no_hash_link, cached_archives_for_no_hash_link),
        (correct_link, cached_archives_for_correct_link),
        (incorrect_link, cached_archives_for_incorrect_link),
    ]:
        link = Link(url)
        archives = chef.get_cached_archives_for_link(link)
        assert set(archives) == answer


def test_get_cache_directory_for_link(config):
    chef = Chef(
        config,
        MockEnv(
            marker_env={"interpreter_name": "cpython", "interpreter_version": "3.8.3"}
        ),
    )

    directory = chef.get_cache_directory_for_link(
        Link("https://files.python-poetry.org/poetry-1.1.0.tar.gz")
    )
    expected = Path(
        "/foo/artifacts/ba/63/13/283a3b3b7f95f05e9e6f84182d276f7bb0951d5b0cc24422b33f7a4648"
    )

    assert expected == directory
