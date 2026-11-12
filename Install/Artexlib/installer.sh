g++ -c -fPIC calculadora.cpp -o calculadora.o
g++ -shared -o libcalculadora.so calculadora.o

sudo cp calculadora.h /usr/local/include/
sudo cp libcalculadora.so /usr/local/lib/
sudo ldconfig
