1. install the venv using python -m venv venv      
2. activate the venv using  .\.\venv\Scripts\Activate.ps1
3. move to backend
4. install the dependencies using python -m pip install -r requirements.txt
5. run in one terminal backend :  fastapi dev main.py and open http://127.0.0.1:8000/docs
6. run in another terminal frontend: py -m http.server 5500 and open http://127.0.0.1:5500/index.html