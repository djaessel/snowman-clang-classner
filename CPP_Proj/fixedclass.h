#ifndef FIXEDCLASS_H
#define FIXEDCLASS_H

#include <QString>

#include "fixedfunction.h"

using namespace std;

class FixedClass
{
private:
  QString name;
  vector<FixedFunction> functions;
public:
  FixedClass(){this->name = "NO_NAME";}
  FixedClass(QString name) {this->name = name;}
  QString getName() {return this->name;}
  void addFunction(FixedFunction function) {functions.push_back(function);}
  FixedFunction getFunction(int index) {return functions[index];}
  vector<FixedFunction> getFunctions() {return functions;}
};

#endif // FIXEDCLASS_H
