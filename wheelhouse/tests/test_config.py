try:
    import ConfigParser as configparser
except ImportError:
    import configparser
import tempfile

from pathlib import Path
import mock

from wheelhouse.config import Config


class TestConfig(object):

    class ConfigParserMock(object):
        def get(self, section, item):
            return '/'.join([section, item])

    class ConfigParserMockError(object):
        def get(self, section, item):
            raise configparser.NoOptionError(section, item)

    def test_default_config_location(self):
        assert Config(True).config_fname == 'wheelhouse.ini'

    def test_walk_paths_contains_config_fname(self):
        config = Config(True)

        for path in config.walk_paths():
            assert config.config_fname == path.name

    def test_walk_paths_resovles_to_root(self):
        config = Config(True)
        assert len(config.walk_paths()) == len(Path.cwd().parts)

    def test_set_project_root_finds_first_project_config_file(self):
        config = Config(True)
        tmp_file = tempfile.NamedTemporaryFile()
        tmp_file_path = Path(tmp_file.name)

        # Mock out the walk_path call
        config.walk_paths = lambda: [
            Path.cwd().joinpath('imageinaryfile.txt'),
            tmp_file_path,  # expected file
            Path('/a/fake/file/that/shouldnt/exist')
        ]

        config.set_project_root()

        assert config.project_root_dpath == tmp_file_path.resolve().parent

    @mock.patch('wheelhouse.config.appdirs')
    def test_search_fpaths_returns_string_of_appdir_and_walk_paths(self, appdirs_mock):
        appdirs_mock.user_config_dir = Path.cwd()

        config = Config(True)
        config.walk_paths = lambda: [
            Path.cwd().joinpath('imageinaryfile.txt'),
        ]

        assert config.search_fpaths() == [
            str(Path.cwd() / config.config_fname),
            str(Path.cwd().joinpath('imageinaryfile.txt')),
        ]

    def test_set_defaults_setsup_config_parser_defaults(self):
        config = Config(True)
        config.cp = configparser.SafeConfigParser()

        assert config.cp.sections() == []

        config.set_defaults()

        assert config.cp.sections() == ['aliases', 'wheelhouse']
        assert config.cp.get('wheelhouse', 'requirement_files') == ''
        assert config.cp.get('wheelhouse', 'requirements_path') == 'requirements'
        assert config.cp.get('wheelhouse', 'wheelhouse_path') == 'requirements/wheelhouse'
        assert config.cp.get('wheelhouse', 'pip_bins') == 'pip'

    def test_load_files_inits_safe_config_parser(self):
        config = Config(True)
        config.cp = None

        config.load_files()
        assert isinstance(config.cp, configparser.SafeConfigParser)

    def test_load_files_sets_found_fpaths(self):
        config = Config(True)
        tmp_file = tempfile.NamedTemporaryFile()
        config.search_fpaths = lambda: [tmp_file.name]

        config.load_files()
        assert config.found_fpaths == [tmp_file.name]

    def test_load_files_reads_found_files(self):
        config = Config(True)
        tmp_file = tempfile.NamedTemporaryFile()
        tmp_file.write('[wheelhouse]\nrequirement_files=test')
        tmp_file.flush()

        config.search_fpaths = lambda: [tmp_file.name]
        config.load_files()
        assert config.cp.get('wheelhouse', 'requirement_files') == 'test'

    def test_requirements_dpath(self):
        config = Config(True)
        config.cp = self.ConfigParserMock()
        config.project_root_dpath = Path('/')

        assert config.requirements_dpath == Path('/wheelhouse/requirements_path')

    def test_wheelhouse_dpath(self):
        config = Config(True)
        config.cp = self.ConfigParserMock()
        config.project_root_dpath = Path('/')

        assert config.wheelhouse_dpath == Path('/wheelhouse/wheelhouse_path')

    def test_requirement_files(self):
        config = Config(True)
        config.cp = self.ConfigParserMock()
        config.project_root_dpath = Path('/')

        assert config.requirement_files == [
            Path('/wheelhouse/requirements_path/wheelhouse/requirement_files')
        ]

    def test_pip_bins(self):
        config = Config(True)
        config.cp = self.ConfigParserMock()
        config.project_root_dpath = Path('/')

        assert config.pip_bins == ['wheelhouse/pip_bins']

    def test_alias_sub(self):
        config = Config(True)
        config.cp = self.ConfigParserMock()

        values = config.alias_sub(['test', 'values'])

        assert values == ['aliases/test', 'aliases/values']

    def test_alias_sub_throws_uses_name_with_error(self):
        config = Config(True)
        config.cp = self.ConfigParserMockError()

        assert config.alias_sub(['test']) == ['test']
