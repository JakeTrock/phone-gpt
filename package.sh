rm -v *.zip
pip install -r requirements.txt -t ./package
cd package
zip -r ../lambda_function.zip .
cd ..
zip -g lambda_function.zip lambda_function.py
zip -g lambda_function.zip setup.py
rm -rfv package