# Run Lantern API locally

Start Lantern API on port 4310 with this command after you complete the prerequisites:

```sh
python -m lantern serve --port 4310
```

## Prerequisites

- Python 3.11+.
- The fictional Lantern package is available in your Python environment.
- A valid token for the fictional service is available to you.
- Port 4310 is available.

WARNING: Never commit LANTERN_TOKEN.

## Steps

1. Set the `LANTERN_TOKEN` environment variable to your token in your current shell.
2. Run `python -m lantern serve --port 4310`. Keep this process active.
3. Open `http://127.0.0.1:4310/health` in a browser. Check the response status with the browser's network tools.

## Expected result

The request to `http://127.0.0.1:4310/health` returns `HTTP 200`.
This response confirms that the local service responds to the health request.

## Troubleshooting

Symptom: The browser cannot connect to the health address.

Cause: The Lantern API process is not active.

Fix: Run `python -m lantern serve --port 4310` and keep the process active. Repeat step 3.
