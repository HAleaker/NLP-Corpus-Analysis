from eea.corpus.utils import hashed_id


def component_phash_id(file_name, text_column, pipeline):
    """ Calculate a hash as consistent uid based on the pipeline
    """
    salt = [(file_name, text_column)]
    for name, step_id, settings in pipeline:
        if isinstance(settings, dict):
            settings = settings.copy()
            settings.pop('schema_position', None)
            settings.pop('schema_type', None)
            settings = sorted(settings.items())
        salt.append((name, settings))
    return hashe