=======================================
Setting up uWsgi tuning for MITx Online
=======================================

This setup satisfies the testing to help with tuning as mentioned in this `Discusssion Post <https://github.com/mitodl/hq/discussions/393>`_

Largely borrowed from work on OCW studio:

| `Adding uWSGI stats <https://github.com/mitodl/ocw-studio/pull/1898/>`_
| `Tuning the App <https://github.com/mitodl/ocw-studio/pull/1886/>`_


******************
To set up locally:
******************

Set up uwsgitop
---------------
1. Set UWSGI_RELOAD_ON_RSS in your .env to a high value (e.g. 500)
2. Set UWSGI_MAX_REQUESTS in your .env to a high value (e.g. 10000)
3. ``docker compose build``
4. ``docker compose up``
5. In a new terminal window/tab, ``docker compose exec web uwsgitop /tmp/uwsgi-stats.sock``
6. You should see your application's memory usage without usage. Ready to go.


Set up Locust
-------------
1. Install Locust: ``docker compose run --rm web poetry add locust``
2. Add locust to your docker-compose.yml locally, under services:

.. code-block:: shell

	locust:
	  image: locustio/locust
	  ports:
	    - "8089:8089"
	  volumes:
	    - ./:/src
	  command: >
	    -f /src/locustfile.py

3. Add the following to the web block, at the level of, and directly after, ``build``:

.. code-block:: shell

    deploy:
      resources:
        limits:
          cpus: "2"
          memory: "1g"

4. Add locustfile.py. There is an example file at ``locustfile.py.example`` in the root of the repo.  ``cp locustfile.py.example locustfile.py`` will copy it over as is. Change variables and/or add tests as needed.

Put it all together
-------------------

1. Run ``docker-compose build``
2. Run ``docker-compose up``
3. You can use locust from ``http://0.0.0.0:8089/`` in a browser
4. You can use uwsgitop in a terminal with ``docker compose exec web uwsgitop /tmp/uwsgi-stats.sock``

******************
To test:
******************

For each step of the testing, you will have 2 tools open. These are:
- uWSGI via ``docker compose exec web uwsgitop /tmp/uwsgi-stats.sock`` in terminal, and
- Locust via ``http://0.0.0.0:8089/`` in your browser

Start the app with your base, starting values and run tests in an increasing frequency while keeping note of the following values:
- In uwsgitop:
  - AVG - average request time
  - RSS - worker resident set size (over simply: how big the worker gets to handle requests)
  - REQ - how many requests the worker has made
- In Locust:
  - Median & Average ms - in my experience these are close, but if they are not in yours, it might be a good indicator
  - # of requests which will be helpful for the next item
  - # of fails and when failures start popping up

You will want to look at these at the start, as things are progressing take some touch points, when failures start
popping up, and once the workers reach your current reload-on-rss and max-requests values.

I stepped up my tests:
number of users: 1, 100, 250, 500
spawn rate: 1, 5, 10, 50

I found that this gave me a little variability around what was spawning when.

Once you've run a set of tests with the starting values, you will find that the rss value might be out of range. Take
note of the starting value and teh breaking value and go a bit under the breaking value.  Take this new starting
reload_on_rss value and divide available memory by it & round down to determine workers. You will then need to tune your
threads up and down to find a place where you're able to keep response time low, but also workers aren't reloading so
often it's disruptive.  This is where the response times will come in handy as well as noting how many requests you get
between reloads.

This is largely a process of trial and error, with a starting set point from which you can tune the value until you find
balance.

