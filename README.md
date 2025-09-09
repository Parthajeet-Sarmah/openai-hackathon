# Local AI Assistant and Event tracker - Made for OpenAI Open Model hackathon

## Scope of this project
To build a basic, functional local AI assistant and event tracker using `gpt-oss` which can listen to different events of the system for the particular user and generate valuable insights based on the events (**for current scope, the mouse, the keyboard and process creation and termination are implemented**).

## Technologies used
- Python, its libraries and frameworks (FastAPI, PySide6, pyinput etc.)
- Docker

## Testing instructions (tested on Ubuntu 22.04)

### Prerequisites
- Docker must be installed for the system
- The `gpt-oss` model used here is a quantized model (for better performance) of the original gpt-oss-20B model by OpenAI, which can be found here at HuggingFace: [bartowski/openai_gpt-oss-20b-GGUF ](https://huggingface.co/bartowski/openai_gpt-oss-20b-GGUF/blob/main/openai_gpt-oss-20b-MXFP4.gguf)
- After downloading the model, paste it under a `models/` folder in the root of the project
- I am using PySide6 Qt for the frontend, which require permissions to access the monitor for display. For Ubuntu, this is done by the command in the terminal
```
$ xhost +local:activity-monitor
```

### Sample tree for Project structure (some folders are temporary folders, so they may not exist in your project)
```
.
├── ai_inference
│   ├── event_fetcher.py
│   ├── __init__.py
│   ├── model_inference.py
│   ├── prompt_builder.py
│   ├── prompt_templates
│   │   └── summary.jinja
│   └── __pycache__
│       ├── event_fetcher.cpython-310.pyc
│       ├── __init__.cpython-310.pyc
│       ├── model_inference.cpython-310.pyc
│       └── prompt_builder.cpython-310.pyc
├── backend
│   ├── api_server.py
│   └── __pycache__
│       └── api_server.cpython-310.pyc
├── data_ingestor
│   └── main.py
├── docker-compose.app.yaml
├── docker-compose.yml
├── Dockerfile
├── event_collector
│   ├── keyboard_event_collector.py
│   ├── main.py
│   ├── mouse_event_collector.py
│   └── process_event_collector.py
├── frontend
│   └── main.py
├── models
│   └── openai_gpt-oss-20b-MXFP4.gguf
├── README.md
├── requirements.txt
└── start.sh
```

### Steps for testing

- Provide correct permissions for the monitor. For Ubuntu, this is done by writing this command in the terminal
```
$ xhost +local:activity-monitor
```
- Build and run the `docker-compose.yaml` file, which sets up the model with the `llama-server` (make sure the model name matches in the `models` folder and the one in the `volumes` section of `docker-compose.yml`)
```
$ docker compose up --build -d
```
***NOTE:  It is necessary that the model has completely done its setup, before writing executing the next instruction as the frontend will immediately fire an API request to the model server on start, check the docker logs of the container to confirm.***

- Build and the run the application's docker compose file, `docker-compose.app.yaml`, which initializes the backend and then the frontend.
```
$ docker compose -f docker-compose.app.yaml up --build -d
```
- Upon successful startup, you can do different actions on ***either your keyboard or mouse, or start/close some windows and process***. The application will track this data and feed it to the LLM for generating insights every minute.

**NOTE: By default, the events are fetched, followed by the generation of insights by the model at a fixed interval of 1 minute**

### Future scope (What it could possibly become)
- Fine-tune the prompts to generate better insights
- Modify the system to construct new information and form insights based on the given event data
- System resource monitoring (CPU temp, system vitals etc.)
- Try to add infographics, perhaps!
- **Detection and notification of suspicious background input and processes**
- Improve UX
- Other stuff that I haven't thought about :)