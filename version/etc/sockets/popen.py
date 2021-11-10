import subprocess

process = subprocess.Popen([r'C:\path\to\app.exe', 'arg1', '--flag', 'arg'])

process = subprocess.Popen([r'C:\path\to\app.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# This will block until process completes
data = process.read().strip() # 파일에서 저장된 결과를 읽어 data에 저장합니다.

stdout, stderr = process.communicate()
print(stdout)
print(stderr)

process.close()