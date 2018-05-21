# datadoggy

**Visualizing some Datadog rare-time series for Buildhub.**

To use this you need an `API_KEY` and an `APP_KEY` environment variable.

Put them in a `.env` file so it looks something like this:

```
API_KEY=127ab5f3h04gdce896ha68045df932gb71ec
APP_KEY=f83b07hb82b70144h71caga7hh3b25
```

Install the dependencies:

```sh
pip install -r requirements.txt
```

Run it:

```
python metrics.py
```
