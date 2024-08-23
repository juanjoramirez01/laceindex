import flask
from flask import request, jsonify, render_template, redirect, url_for, send_from_directory
import pandas as pd
import numpy as np
import os

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["TEMPLATE_FOLDER"] = "C:\\Users\\jhoan\\Desktop\\dock"
# Crear la carpeta de subida si no existe
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Definir función para calcular el índice LACE
def calcular_lace(fila, df):
    lengthStayDays = max((fila['Fecha egreso'] - fila['Fecha ingreso']).days, 1)
    admissionAcuity = 2 if fila['Tipo de ingreso'] == 'Urgente' else 1
    emergencyVisits = fila['Num ingresos a urgencias en los ultimos 6 meses']
    enfermedades_paciente = filtrar(fila)

    # Calcular índice de Charlson
    totalC = formatear(enfermedades_paciente, df)

    if lengthStayDays == 1:
        scoreL = 1
    elif lengthStayDays == 2:
        scoreL = 2
    elif lengthStayDays == 3:
        scoreL = 3
    elif lengthStayDays >= 4 and lengthStayDays <= 6:
        scoreL = 4
    elif lengthStayDays >= 7 and lengthStayDays <= 13:
        scoreL = 5
    elif lengthStayDays >= 14:
        scoreL = 7
    else:
        scoreL = 0

    scoreA = 3 if admissionAcuity == 2 else 0

    if totalC == 1:
        scoreC = 1
    elif totalC == 2:
        scoreC = 2
    elif totalC == 3:
        scoreC = 3
    elif totalC >= 4:
        scoreC = 5
    else:
        scoreC = 0

    scoreE = min(emergencyVisits, 4)

    scoreTotal = scoreL + scoreA + scoreC + scoreE

    if 1 <= scoreTotal <= 4:
        risk_level = 'Riesgo bajo de readmision'
    elif 5 <= scoreTotal <= 9:
        risk_level = 'Riesgo medio de readmision'
    elif scoreTotal >= 10:
        risk_level = 'Riesgo alto de readmision'
    else:
        risk_level = 'Error'

    return scoreTotal, risk_level, totalC

# Definición de funciones para el cálculo del índice de Charlson
def filtrar(fila):
    lista = []
    for i in fila:
        if isinstance(i, str) and (len(i) == 3 or len(i) == 4):
            lista.append(i)
    return lista

def formatear(fila, df):
    disease = []
    score = []

    for i in fila:
        if i[-1] == 'X':
            i = i[:-1]
        disease.append(df[df['C'] == i.upper()].values[0][5])
    new_disease = set(disease)
    new_disease = list(new_disease)

    if 'DCC' in new_disease and 'DSC' in new_disease:
        new_disease.remove('DSC')

    if 'TSM' in new_disease and 'TNM' in new_disease:
        new_disease.remove('TNM')

    if 'EHS' in new_disease and 'EHL' in new_disease:
        new_disease.remove('EHL')

    for i in new_disease:
        score.append(df[df['F'] == i].values[0][4])
    totalC = sum(score)

    return totalC

# Cargar el .xls
db = 'C:\\Users\\jhoan\\Desktop\\dock\\CIE-10.xls'
df = pd.read_excel(db)

# Cargar el .xlsx
db2 = "C:\\Users\\jhoan\\Desktop\\dock\\Información para charlson index.xlsx"
df2 = pd.read_excel(db2)

# Ajustar los nombres de las filas y de las columnas para que coincidan con el .xls
df.index = df.index + 2
new_df = df.sort_index()
new_df.columns = ['A', 'B', 'C', 'D']
new_df['E'] = 0
new_df['F'] = 'N/A'

# Definir las enfermedades y sus códigos
new_df.loc[3207:3216, ['E', 'F']] = (1, 'IAM')
new_df.loc[3229:3237, ['E', 'F']] = (1, 'IAM') #Insuficiencia congestiva cardíaca
new_df.loc[3346:3348, ['E', 'F']] = (1, 'ICC')
new_df.loc[3299:3312, ['E', 'F']] = (1, 'ICC')
new_df.loc[[3190, 3191, 3194, 3196], ['E', 'F']] = (1, 'ICC') #Enfermedad vascular periférica
new_df.loc[3427:3451, ['E', 'F']] = (1, 'EVP')
new_df.loc[3460:3476, ['E', 'F']] = (1, 'EVP') #Enfermedad cerebrovascular
new_df.loc[3362:3426, ['E', 'F']] = (1, 'ECV')
new_df.loc[2578:2593, ['E', 'F']] = (1, 'ECV')#Demencia
new_df.loc[2042:2063, ['E', 'F']] = (1, 'DEM')
new_df.loc[2527:2535, ['E', 'F']] = (1, 'DEM')#Enfermedad pulmonar obstructiva crónica
new_df.loc[3658:3711, ['E', 'F']] = (1, 'EPOC') #Enfermedad del tejido conectivo
new_df.loc[4545:4557, ['E', 'F']] = (1, 'ETC')
new_df.loc[4699:4736, ['E', 'F']] = (1, 'ETC') #Úlcera péptica
new_df.loc[3893:3928, ['E', 'F']] = (1, 'UP') #Enfermedad hepática leve
new_df.loc[4076:4091, ['E', 'F']] = (1, 'EHL')
new_df.loc[4095:4125, ['E', 'F']] = (1, 'EHL')
new_df.loc[452:456, ['E', 'F']] = (1, 'EHL') #Diabetes
new_df.loc[1728:1777, ['E', 'F']] = (2, 'DCC')
new_df.loc[[1737, 1747, 1757, 1767, 1777], ['E', 'F']] = (1, 'DSC') #Hemiplejia
new_df.loc[2711:2733, ['E', 'F']] = (2, 'HEM') #Enfermedad renal moderada o severa
new_df.loc[5190:5193, ['E', 'F']] = (2, 'ERS')
new_df.loc[[3192, 3195], ['E', 'F']] = (2, 'ERS') #Leucemia
new_df.loc[1192:1227, ['E', 'F']] = (2, 'LEU') #Linfoma
new_df.loc[1155:1185, ['E', 'F']] = (2, 'LIN') #Tumor no metastásico
new_df.loc[784:1127, ['E', 'F']] = (2, 'TNM')
new_df.loc[1186:1191, ['E', 'F']] = (2, 'TNM')
new_df.loc[1228:1234, ['E', 'F']] = (2, 'TNM') #Enfermedad hepática moderada o severa
new_df.loc[[3504, 3505, 4092, 4093, 4094], ['E', 'F']] = (3, 'EHS') #Tumor sólido metastásico
new_df.loc[1128:1154, ['E', 'F']] = 6, 'TSM' #VIH
new_df.loc[459:484, ['E', 'F']] = (6, 'VIH') #Recortar los códigos CIE10 que tengan un símbolo al final, eliminando este
new_df['C'] = new_df['C'].str.slice(0, 4) #Filtrar la fila para eliminar valores innecesarios ('S', nan)

# Página de inicio
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download_template', methods=['GET'])
def download_template():
    return send_from_directory(directory=app.config["TEMPLATE_FOLDER"], path='plantilla.xlsx', as_attachment=True)

# Página de carga de archivos
@app.route('/upload')
def upload_page():
    return render_template('lace_descarga.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        process_file(file_path)
        return redirect(url_for('upload_page'))  # Redirigir a la misma página tras el procesamiento

def process_file(file_path):
    df2 = pd.read_excel(file_path)
    df2_clean = df2.copy()
    df2_clean['LACE'], df2_clean['LACE_Risk_Level'], df2_clean['Charlson_Index'] = zip(*df2_clean.apply(lambda fila: calcular_lace(fila, new_df), axis=1))
    df2_clean.fillna(value=np.nan, inplace=True)
    df2_clean_filtered = df2_clean.dropna(axis=1, how='all')
    df2_clean_filtered = df2_clean_filtered.where(pd.notnull(df2_clean_filtered), None)
    df2_clean_filtered = df2_clean_filtered.loc[:, ~df2_clean_filtered.isin(['S']).any()]
    df2_clean_filtered = df2_clean_filtered.dropna(axis=1, how='all')
    df2_clean_filtered['Fecha ingreso'] = pd.to_datetime(df2_clean_filtered['Fecha ingreso']).dt.strftime('%Y-%m-%d')
    df2_clean_filtered['Fecha egreso'] = pd.to_datetime(df2_clean_filtered['Fecha egreso']).dt.strftime('%Y-%m-%d')
    
    # Guardar el DataFrame procesado en una variable global
    global df2_clean_global
    df2_clean_global = df2_clean_filtered
    return df2_clean_filtered.to_dict(orient='records')


@app.route('/api/v1/lace', methods=['GET'])
def get_lace():
    global df2_clean_global
    if df2_clean_global is not None:
        return jsonify(df2_clean_global.to_dict(orient='records'))
    else:
        return jsonify({"error": "No data processed"})

@app.route('/api/v1/upload_lace', methods=['POST'])
def upload_lace():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Procesa el archivo y calcula el índice LACE
        lace_results = process_file(file)
        return jsonify(lace_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Página de ingreso manual de datos
@app.route('/manual')
def manual():
    return render_template('lace.html')

@app.route('/api/v1/manual_lace', methods=['POST'])
def calculate_manual_lace():
    data = request.form
    enfermedades_paciente = [enfermedad.strip() for enfermedad in data.get('enfermedades').split(',')]
    lengthStayDays = int(data.get('lengthStayDays'))
    admissionAcuity = int(data.get('admissionAcuity'))
    emergencyVisits = int(data.get('emergencyVisits'))

    # Filtrar códigos de enfermedades válidos y calcular el índice de Charlson
    totalC = formatear(filtrar(enfermedades_paciente), new_df)

    # Calcular el índice LACE
    if lengthStayDays == 1:
        scoreL = 1
    elif lengthStayDays == 2:
        scoreL = 2
    elif lengthStayDays == 3:
        scoreL = 3
    elif lengthStayDays >= 4 and lengthStayDays <= 6:
        scoreL = 4
    elif lengthStayDays >= 7 and lengthStayDays <= 13:
        scoreL = 5
    elif lengthStayDays >= 14:
        scoreL = 7
    else:
        scoreL = 0

    if admissionAcuity == 2:
        scoreA = 3
    else:
        scoreA = 0

    if totalC == 1:
        scoreC = 1
    elif totalC == 2:
        scoreC = 2
    elif totalC == 3:
        scoreC = 3
    elif totalC >= 4:
        scoreC = 5
    else:
        scoreC = 0

    if emergencyVisits == 1:
        scoreE = 1
    elif emergencyVisits == 2:
        scoreE = 2
    elif emergencyVisits == 3:
        scoreE = 3
    elif emergencyVisits >= 4:
        scoreE = 4
    else:
        scoreE = 0

    scoreTotal = scoreL + scoreA + scoreC + scoreE

    if scoreTotal >= 1 and scoreTotal <= 4:
        risk_level = 'Low risk of readmission'
    elif scoreTotal >= 5 and scoreTotal <= 9:
        risk_level = 'Medium risk of readmission'
    elif scoreTotal >= 10:
        risk_level = 'High risk of readmission'
    else:
        risk_level = 'Error'

    return jsonify({
        'Lace score': scoreTotal,
        'risk_level': risk_level,
        'charlson_score': totalC
    })

if __name__ == '__main__':
    df2_clean_global = None
    app.run(host="0.0.0.0", port=5000)
