#include "functionanalyzer.h"
#include "classstorer.h"


map<QString, QStringList> FunctionAnalyzer::addUsedClassImports(map<QString, FixedClass> &classes, vector<RawClass> &rawClasses)
{
  map<QString, QStringList> includes;
  foreach (auto cls, classes) {
      includes.insert_or_assign(cls.first, this->addUsedClassImports(cls.first, classes, rawClasses));
  }
  return includes;
}

QStringList FunctionAnalyzer::addUsedClassImports(QString cls, map<QString, FixedClass> &classes, vector<RawClass> &rawClasses)
{
  QStringList includes;

  foreach (RawClass obj, rawClasses) {
      foreach (RawFunction rawFunc, obj.getFunctions()) {
          foreach (auto cls2, classes) {
              QString declar = rawFunc.getDeclar();
              if (declar.contains(cls2.first) && !includes.contains(cls2.first)) {
                  if (declar.contains("(" + cls2.first + " ") ||
                      declar.contains("(" + cls2.first + "*") ||
                      declar.contains(" " + cls2.first + " ") ||
                      declar.contains(" " + cls2.first + "*"))
                    includes.append(cls2.first);
              }
          }
      }
  }

  foreach (FixedFunction func, classes[cls].getFunctions()) {
      foreach (QString line, func.getCodeLines()) {
          foreach (auto cls2, classes) {
              if (line.contains(cls2.first) && !includes.contains(cls2.first)) {
                  if (line.contains(" " + cls2.first + "*") ||
                      line.contains(" " + cls2.first + " ") ||
                      line.contains(" " + cls2.first + "("))
                    includes.append(cls2.first);
              }
          }
      }
  }

  return includes;
}

map<QString, FixedClass> FunctionAnalyzer::findOriginalClass(map<QString, FixedClass> &classes)
{
  map<QString, FixedClass> fixedClasses;
  foreach (auto cls, classes) {
      fixedClasses.insert_or_assign(cls.first, this->findOriginalClass(cls.first, classes));
  }
  return fixedClasses;
}

FixedClass FunctionAnalyzer::findOriginalClass(QString cls, map<QString, FixedClass> &classes)
{
  FixedClass fixedClass;
  map<QString, QString> tracerx;
  //bool foundSomething = false;

#ifdef DEBUGMODE
  cout << "Analyzing " << cls.toStdString().c_str() << "...";
#endif

  foreach (FixedFunction func, classes[cls].getFunctions()) {
      FixedFunction fixedFunc(func.getName());
      bool declarMode = false;
      foreach (QString line, func.getCodeLines()) {
          if (line.contains("possible pointer usage or inline declarations")) declarMode = true;
          else if (declarMode) {
              if (!line.contains("}"))
                fixedFunc.insertCodeLine(1, line);
              else
                fixedFunc.addCodeLine(line);
          } else {
              foreach (auto cls2, classes) {
                  foreach (FixedFunction func2, cls2.second.getFunctions()) {
                      QString lll = "->" + func2.getName();
                      if (line.contains(lll)) {
                          bool skip = false;
                          foreach (auto trx, tracerx) {
                              if (line.contains(trx.first + lll)) {
                                  skip = true;
                                  break;
                              }
                          }

                          if (!skip && (line.contains(lll + "(") ||
                                        line.contains(lll + ";") ||
                                        line.contains(lll + ")"))) {
                              //if (!foundSomething) {
                              //    cout << cls.toStdString().c_str() << ": [fixing 1]" << endl;
                              //    foundSomething = true;
                              //}
                              //cout << "FOUND TRACE: " << cls2.first.toStdString().c_str() << " " << func2.getName().toStdString().c_str() << " " << line.toStdString().c_str();
                              int idx = line.indexOf(lll);
                              QStringList tmpx = line.left(idx).split(' ');
                              QString tmpx2("");
                              if (tmpx.length() > 0)
                                tmpx2 = tmpx.back();
                              tmpx2 = tmpx2.remove(QRegExp("^([&]+)")).remove(QRegExp("^([*]+)")); // remove extras # TODO: check again alter
                              QString func2Name = func2.getName();
                              if (classes[cls].getFunction(func2Name).getName() != nullptr) {
                                  line = line.replace(tmpx2 + "->" + func2Name, "this->" + func2Name);
                              } else if (tmpx2.length() > 0 && tracerx.count(tmpx2) <= 0) {
                                  tracerx.insert_or_assign(tmpx2, cls2.first);
                              } else {
                                  cout << cls2.first.toStdString().c_str() << " > ERROR: EMPTY RDI_OBJECT! " << line.remove("\n").toStdString().c_str(); // FIXME: fix this in original generation of these rdi->func() lines
                              }
                          }
                      }
                  }
              }
          }

          if (!declarMode)
            fixedFunc.addCodeLine(line);
      }

    fixedClass.addFunction(fixedFunc);
  }

#ifdef DEBUGMODE
    cout << "DONE" << endl;
    cout << "Fixing " << cls.toStdString().c_str() << "...";
#endif

    QStringList removeTrace;
    foreach (auto trace, tracerx) {
        bool isDigit = true;
        foreach (auto c, trace.first) {
            if (!c.isDigit()) {
                isDigit = false;
                break;
            }
        }
        if (isDigit) {
            //cout << "Found wrong trace: " << trace.first.toStdString().c_str() << endl;
            removeTrace.append(trace.first);
        }
    }
    foreach (QString t, removeTrace) {
        tracerx.erase(t);
    }

    foreach (FixedFunction func, fixedClass.getFunctions()) {
        //foundSomething = false;
        int i = 0;
        QStringList newLines = func.getCodeLines();
        foreach (QString line, func.getCodeLines()) {
            QString linx;
            foreach (auto trace, tracerx) {
                if (line.contains(" " + trace.first + ";")) {
                    linx = line.trimmed().split(';')[0];
                    QStringList declax = linx.split(' ');
                    if (declax.length() <= 2) {
                        //if (!foundSomething) {
                        //    cout << cls.toStdString().c_str() << ": " << func.getName().toStdString().c_str() << " [fixing 2.1]" << endl;
                        //    foundSomething = true;
                        //}
                        line = line.replace(linx + ";", trace.second + "* " + trace.first + ";"); // make pointer for class for now!
                        if (declax[0].contains("STRUCT"))
                          line = line.remove(QRegExp("([\n]+)$")); // was STRUCT before --> " + declax[0] + "\n"

                        newLines[i] = line;

                        //cout << cls.toStdString().c_str() << ": [fixing 2.1] " << trace.first.toStdString().c_str() << " " << line.toStdString().c_str() << endl;
                    }
                } else if (line.contains(trace.first + " = ")) {
                    linx = line.trimmed();
                    linx = linx.split(" = ")[0];
                    QStringList jo = linx.split(' ');
                    if (jo.length() <= 2) {
                        //if (!foundSomething) {
                        //    cout << cls.toStdString().c_str() << ": " << func.getName().toStdString().c_str() << " [fixing 2.2]" << endl;
                        //    foundSomething = true;
                        //}
                        if (jo[0].contains("STRUCT") || ClassStorer::AllValidTypes.contains(jo[0])) {
                            line = line.replace(linx + " = ", trace.second + "* " + trace.first + " = "); // make pointer for class for now!
                            newLines[i] = line;
                            //cout << cls.toStdString().c_str() << ": [fixing 2.2] " << trace.first.toStdString().c_str() << " " << line.toStdString().c_str() << endl;
                        }
                    }
                }
            }
            i++;
        }

        func.setCodeLines(newLines);
        fixedClass.updateFunc(func);
    }

#ifdef DEBUGMODE
  cout << "DONE" << endl;
#endif

  return fixedClass;
}
