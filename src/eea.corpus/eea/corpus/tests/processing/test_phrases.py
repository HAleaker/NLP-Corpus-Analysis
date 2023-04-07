
from unittest.mock import patch, sentinel as S, Mock    # , call,
import pytest


class TestSchema:

    def test_it(self):
        from eea.corpus.processing.phrases.schema import PhraseFinder
        from eea.corpus.processing.phrases.widget import PhraseFinderWidget

        schema = PhraseFinder()
        assert isinstance(schema.widget, PhraseFinderWidget)
        assert len(schema.children) == 5


class TestUtils:

    @patch('eea.corpus.processing.phrases.utils.os.listdir')
    def test_phrase_model_files(self, listdir):
        from eea.corpus.processing.phrases.utils import phrase_model_files

        phash_id = 'abc'
        listdir.return_value = [
            'cba',
            'abc.phras.2',
            'abc.phras.1',
            'abc',
            'abc.phras',
        ]
        res = phrase_model_files('/corpus', phash_id)

        assert res == ['/corpus/abc.phras.1', '/corpus/abc.phras.2']


class TestAsync:

    @patch('eea.corpus.processing.phrases.async.build_phrase_models')
    @patch('eea.corpus.processing.phrases.async.build_pipeline')
    @patch('eea.corpus.processing.phrases.async.corpus_base_path')
    def test_build_phrases_job(self, corpus_base_path, build_pipeline,
                               build_phrase_models):

        from eea.corpus.processing.phrases.async import build_phrases

        corpus_base_path.return_value = '/corpus'
        build_pipeline.return_value = S.content

        build_phrases([S.step1, S.step2],
                      'some.csv', 'text', 'phash_abc', S.settings)

        corpus_base_path.assert_called_once_with('some.csv')

        assert build_pipeline.call_args[0] == ('some.csv', 'text', [S.step1])
        assert build_phrase_models.call_args[0] == (
            S.content, '/corpus/phash_abc.phras', S.settings
        )

    @patch('eea.corpus.processing.phrases.phrases.Phrases')
    def test_build_phrase_models(self, Phrases):
        from eea.corpus.processing.phrases.phrases import build_phrase_models
        from textacy.doc import Doc

        content = [Doc('hello'), Doc('world')]

        phrases = Phrases()
        Phrases.return_value = phrases

        build_phrase_models(content, '/corpus/some.csv.phras', {'level': 2})

        # call count should be 1, but we called above once
        assert Phrases.call_count == 2
        assert phrases.save.call_args[0] == ('/corpus/some.csv.phras.2',)

        build_phrase_models(content, '/corpus/some.csv.phras', {'level': 3})

        # call count should be 1, but it accumulates with the 2 above
        assert Phrases.call_count == 4
        assert phrases.save.call_args[0] == ('/corpus/some.csv.phras.3',)

    @pytest.mark.slow
    def test_build_phrase_models_real(self, doc_content_stream):

        from eea.corpus.processing.phrases.phrases import build_phrase_models
        from eea.corpus.utils import rand
        from gensim.models.phrases import Phrases
        from itertools import tee, chain
        import os.path
        import tempfile

        content_A, content_B, test_A = tee(doc_content_stream, 3)

        # proof that the simple_content_stream can be used for phrases
        # ph_model = Phrases(content_A)
        # phrases = list(ph_model.export_phrases(sents))
        # assert phrases[0][0].decode('utf-8') == 'freshwater resources'

        base_dir = tempfile.gettempdir()
        b_name = rand(10)
        base_path = os.path.join(base_dir, b_name)
        build_phrase_models(content_A, base_path, {'level': 2})

        assert b_name + '.2' in os.listdir(base_dir)
        assert not (b_name + '.3' in os.listdir(base_dir))
        os.remove(base_path + '.2')

        t_name = rand(10)
        base_path = os.path.join(base_dir, t_name)
        build_phrase_models(content_B, base_path, {'level': 3})

        assert t_name + '.2' in os.listdir(base_dir)
        assert t_name + '.3' in os.listdir(base_dir)

        pm2 = Phrases.load(base_path + '.2')
        pm3 = Phrases.load(base_path + '.3')

        os.remove(base_path + '.2')
        os.remove(base_path + '.3')

        # an iterator of sentences, each a list of words
        test_A = chain.from_iterable(doc.tokenized_text for doc in test_A)
        trigrams = pm3[pm2[test_A]]
        words = chain.from_iterable(trigrams)
        w2, w3 = tee(words, 2)

        bigrams = [w for w in w2 if w.count('_') == 1]
        assert len(bigrams) == 27622
        assert len(set(bigrams)) == 2060

        trigrams = [w for w in w3 if w.count('_') == 2]
        assert len(trigrams) == 11268
        assert len(set(trigrams)) == 706

        assert 'freshwater_resources' in bigrams
        assert 'water_stress_conditions' in trigrams


class TestProcess:

    @patch('eea.corpus.processing.phrases.process.corpus_base_path')
    def test_cached_phrases_no_files(self,
                                     corpus_base_path,
                                     doc_content_stream):
        from eea.corpus.processing.phrases.process import cached_phrases
        from pkg_resources import resource_filename

        base_path = resource_filename('eea.corpus', 'tests/fixtures/')
        corpus_base_path.return_value = base_path

        # we want the B.phras.* files in fixtures
        env = {'phash_id': 'X', 'file_name': 'ignore'}
        settings = {}

        stream = cached_phrases(doc_content_stream, env, settings)
        with pytest.raises(StopIteration):
            next(stream)

    @pytest.mark.slow
    @patch('eea.corpus.processing.phrases.process.corpus_base_path')
    def test_cached_phrases_cached_files(self,
                                         corpus_base_path,
                                         doc_content_stream):

        # TODO: this test should be improved. Text quality should be tested
        from eea.corpus.processing.phrases.process import cached_phrases
        from pkg_resources import resource_filename

        base_path = resource_filename('eea.corpus', 'tests/fixtures/')
        corpus_base_path.return_value = base_path

        # we want the B.phras.* files in fixtures
        env = {'phash_id': 'B', 'file_name': 'ignore'}
        settings = {}

        stream = cached_phrases(doc_content_stream, env, settings)
        doc = next(stream)
        assert 'water_stress_conditions' in doc.text
        assert 'positive_development' in doc.text

    @patch('eea.corpus.processing.phrases.process.produce_phrases')
    @patch('eea.corpus.processing.phrases.process.cached_phrases')
    def test_process_yield_from_cache(self,
                                      cached_phrases,
                                      produce_phrases,
                                      simple_content_stream):

        from eea.corpus.processing.phrases.process import process

        cached_phrases.return_value = ['hello', 'world']
        env = {'preview_mode': False}
