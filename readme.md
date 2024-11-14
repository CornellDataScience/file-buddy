# How to run

Create a `.env` file in the root directory and copy the contents of `.env.example` into it. Replace the placeholder value with the path to the folder you want to monitor (I linked it to my downloads folder). Note that the container only has read access to this folder.

Ensure that you have docker installed. Run:

```
docker compose up --build
```

Any changes you make to the files in `$HOST_FOLDER` will be logged in the console.

You can also search for image files that you added to the host folder by visiting `http://localhost:8000/docs` and entering a search query in the json body.