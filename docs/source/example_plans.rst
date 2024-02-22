Example plans
=============

Introduction
------------

This is a collection of a couple sample plans, using simulated devices from the :py:mod:`ophyd.sim` module, along with a command-line interface useful for quick testing of runs.

Command-line
------------

Executing :code:`python .../simulated_samples.py -h` should bring up a help message specifying how to make a sample run, like so:

.. code-block::

    usage: simulated_samples.py [-h] [-n NUM] [--kafka-topic KAFKA_TOPIC] [--kafka-bootstrap KAFKA_BOOTSTRAP] {random-1d,gaussian-1d,random-2d,gaussian-2d}

    positional arguments:
      {random-1d,gaussian-1d,random-2d,gaussian-2d}
                            Which program to run.

    options:
      -h, --help            show this help message and exit
      -n NUM, --num NUM     Number of times to run the program. (Default: 1)
      --kafka-topic KAFKA_TOPIC
                            Kafka topic to connect to. (Default: swc-kafka-test)
      --kafka-bootstrap KAFKA_BOOTSTRAP
                            Kafka bootstrap server address to connect to. (Default: localhost:9092)

For instance, executing a plan that generates a gaussian bell over 32 points, and transmits the generated documents to a Kafka broker at IP ``1.2.3.4``, in the ``my_test`` topic, would look like this:

:code:`python .../simulated_samples.py --kafka-topic my_test --kafka-bootstrap 1.2.3.4 gaussian-1d`

, and would generate something like that in a viewer monitoring that topic:

.. image:: /images/sample_gaussian_1d.png

Plans
-----

.. currentmodule:: sophys.common.plans.simulated_samples

.. autofunction:: sample_random_1d

.. autofunction:: sample_gaussian_1d

.. autofunction:: sample_random_2d

.. autofunction:: sample_gaussian_2d

