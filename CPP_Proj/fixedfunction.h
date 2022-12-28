#ifndef FIXEDFUNCTION_H
#define FIXEDFUNCTION_H

#include <QStringList>

class FixedFunction
{
private:
  QString _name;
  QStringList _codeLines;
public:
  FixedFunction(QString name) : _name(name) {}
  void addCodeLine(QString line) {_codeLines.append(line);}
  void setCodeLines(QStringList codeLines) {_codeLines = codeLines;}
  QStringList getCodeLines() {return _codeLines;}
};

#endif // FIXEDFUNCTION_H
