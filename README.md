# NLP Corpus Analysis (alpha stage)

This docker image is based on tools like spaCy, Textacy, pyLDAvis & others to analyse a text corpus, such as the collection of all published documents or any other CSV file with a text column.

It provides a range of Machine Learning and Natural Language Processing algorithms that can be executed over a corpus or its subset.

The project aims to provide these methods over a REST API when feasible.

## Current features

### Compose a text transformation pipeline to prepare a corpus

Upload a CSV file, then click "Create a corpus" to access the pipeline composition page.

### Create and visualise topic models via pyLDAvis.

[Topic Modeling](https://en.wikipedia.org/wiki/Topic_model) technique is used for finding topics. In machine learning and NLP, a topic model is a statistical model for identifying abstract "topics" in a document collection.

[Video demonstration](https://www.youtube.com/watch?v=IksL96ls4o0&t=255s)

![LDA visualisation example](ldavis.png?raw=true "LDA visualisation example")

## How to run:

```
docker-compose build
docker-compose up -d
```

This will start the application server on [localhost:8181](http://0.0.0.0:8181) after some time.

## Corpus Data

The latest dataset