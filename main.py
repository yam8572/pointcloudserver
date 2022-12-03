from flask import render_template
from flask import Flask, request, redirect, url_for, send_file
from flasgger import Swagger
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
# from gevent.pywsgi import WSGIServer
import os
import subprocess
import time
import open3d as o3d

# r'路徑'防止字符轉義
UPLOAD_FOLDER = r'C:\www\pointcloudServer\source'
DOWNLOAD_FOLDER = r'C:\www\pointcloudServer\result'
ALLOWED_EXTENSIONS = set(['pcd','ply','3ds','stl','obj','png','jpg','jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['SWAGGER'] = {
    "title": "Flask API",
    "description": "SWAGGER API",
    "version": "1.0.0",
    "termsOfService": "",
    "hide_top_bar": True
}
# Auth Setting
auth = HTTPBasicAuth()
user = 'awinlab'
pw = 'awinlab'
users = {
    user: generate_password_hash(pw)
}

swagger_template = {
    'securityDefinitions': {
        'basicAuth': {
            'type': 'basic'
        }
    },
}

Swagger(app, template=swagger_template)

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def sort_filelist(dir_path):
    files_list = os.listdir(dir_path)
    # 依時間排序
    files_list = sorted(files_list,  key=lambda x: os.path.getmtime(os.path.join(dir_path, x)))
    return files_list

# filename.rsplit('.', 1)[1] 切出檔案格式 ex.pcd
# 1: maxsplit parameter to 1, will return a list with 2 elements(檔路徑:,.pcd)
@app.route('/')
@auth.login_required
def upload():
    return render_template('upload.html')

@app.route('/uploadfile', methods=['GET', 'POST'])
@auth.login_required
def upload_file():
    """
        Return result folder
        ---
        tags:
          - Node APIs
        produces: application/json,
        responses:
          200:
            description: Merge two Point Cloud files and retrun the result file name 
            examples:
              "Merge two Point Cloud files and retrun the result file name"
    """
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file[]")
        filenames = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                filenames.append(filename)

        timestr = time.strftime("%Y%m%d-%H%M%S")
        output = filenames[0].rsplit('.', 1)[0]+"_"+filenames[1].rsplit('.', 1)[0] # **你的輸出檔案名稱**

        # output = timestr+"_"+filenames[0].rsplit('.', 1)[0]+"_"+filenames[1].rsplit('.', 1)[0] # **你的輸出檔案名稱**
        # output ="new_cloud_bin.ply" # **你的輸出檔案名稱**
        p = subprocess.run(
            [
                # 'python', '**你的程式名稱**', '**根據需求放入一至多個參數**'
                # 'python','global_registration_dir.py', 'cloud_0.pcd', 'cloud_1.pcd', 'cloud_0_cloud_1'
                'python','global_registration_dir.py', filenames[0], filenames[1], output
                
            ]
        )
        # send_file(os.path.join(app.config['DOWNLOAD_FOLDER'],output), as_attachment=True)
        # return send_from_directory(app.config['DOWNLOAD_FOLDER'],output+'.ply')
        # return render_template('files.html', filenames=filenames)
        result_files_list=sort_filelist("result")
        return render_template('fileslist.html', dir_path='result',files=result_files_list)
        # return url_for('list_dir',dir_path='result')
    elif request.method == 'GET':
        source_files_list=sort_filelist("source")
        return render_template('fileslist.html', dir_path='source',files=source_files_list)
        # return "GET"
    else:
        return "no GET/POST"


from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Return uploadfile 
    ---
    tags:
      - Node APIs
    produces: application/json,
    responses:
      200:
        description: source filename 
        examples:
          "cloud_0.pcd"
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route('/download/<filename>')
def download_file(filename):
    """
    Return downloadfile 
    ---
    tags:
      - Node APIs
    produces: application/json,
    responses:
      200:
        description: result filename 
        examples:
          "20221115-164006_cloud_0_cloud_1"
    """
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],filename)

@app.route('/filePath/<foldername>/<filename>')
def getFilePath(foldername,filename):
    """
    Return fileName 
    ---
    tags:
      - Node APIs
    produces: application/json,
    responses:
      200:
        description: Return fileName 
        examples:
          "Return fileName "
    """
    return send_from_directory(foldername,filename)

@app.route('/listdir/<dir_path>')
def list_dir(dir_path):
    """
    Return folderlist 
    ---
    tags:
      - Node APIs
    produces: application/json,
    responses:
      200:
        description: Return folderlist 
        examples:
          "Return folderlist "
    """
    files_list = os.listdir(dir_path)
    # 依時間排序
    files_list = sorted(files_list,  key=lambda x: os.path.getmtime(os.path.join(dir_path, x)))
    return render_template('fileslist.html', dir_path=dir_path, files=files_list)

@app.route('/service')
def service():
    """
    Return pointcloud service
    ---
    tags:
      - Node APIs
    produces: application/json,
    responses:
      200:
        description: Return pointcloud service 
        examples:
          "pointcloud service "
    """
    return render_template('service.html')
@app.route('/registration')
def registration():
    """
    Return registration result 
    ---
    tags:
      - Node APIs
    produces: application/json,
    responses:
      200:
        description: Return registration result 
        examples:
          "Return registration result  "
    """
    source_files_list=sort_filelist('source')
    input_1=source_files_list[-2]
    input_2=source_files_list[-1]

    timestr = time.strftime("%Y%m%d-%H%M%S")
    output = input_1.rsplit('.', 1)[0]+"_"+input_2.rsplit('.', 1)[0] # **你的輸出檔案名稱**
    # output = timestr+"_"+input_1.rsplit('.', 1)[0]+"_"+input_2.rsplit('.', 1)[0] # **你的輸出檔案名稱**
    # output ="new_cloud_bin.ply" # **你的輸出檔案名稱**
    p = subprocess.run(
        [
            # 'python', '**你的程式名稱**', '**根據需求放入一至多個參數**'
            'python','global_registration_dir.py', input_1, input_2, output
        ]
    )

    result_files_list=sort_filelist('result')
    return render_template('fileslist.html', dir_path='result',files=result_files_list)

@app.route('/visualize3D/<foldername>/<filename>')
def visualize3D(foldername,filename):
    """
    Return visualize3D 
    ---
    tags:
      - Node APIs
    produces: application/json,
    responses:
      200:
        description: Return visualize3D
        examples:
          "Return visualize3D  "
    """
    pcd = o3d.io.read_point_cloud(foldername+'/'+filename)

    # visualize colored point cloud
    o3d.visualization.draw_geometries([pcd])

    files_list=sort_filelist(foldername)
    return render_template('fileslist.html', dir_path=foldername,files=files_list)

if __name__ == "__main__":
    # http_server = WSGIServer(('', 8080), app)
    # http_server.serve_forever()
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8888)
    app.run(host='0.0.0.0', port=8888, debug=True)