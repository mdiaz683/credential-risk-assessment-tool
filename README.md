# Credential Risk Assessment Proyect
## Introduction
This project is a web application that allows users to assess the risk of a credential based on the information obtained from Telegram, which is username, password, channel and file. The application uses a machine learning model to predict the risk of the credential. The model was trained with a dataset of credentials and their respective risk level. The model was trained using the Kernel Ridge algorithm. The application was developed using the Streamlit library. 

## Instalation
### CLI
1. Download the repository
```bash
git clone <url>
```
2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Run the streamlit app
```bash
streamlit run app.py --server.port=8501
```
4. Open the browser and go to http://localhost:8501

### Docker
1. Download the repository
```bash
git clone <url>
```
2. Build the image
```bash
docker build -t credential-risk-assessment .
```
3. Run the container
```bash
docker run -p 8501:8501 credential-risk-assessment
```
4. Open the browser and go to http://localhost:8501
