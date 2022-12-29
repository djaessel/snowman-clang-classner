#ifndef FUNCTIONANALYZER_H
#define FUNCTIONANALYZER_H

#include <bits/stdc++.h>

#include "specialvals.h"

#include "rawclass.h"
#include "fixedclass.h"

#include <thread>
#include <QRunnable>
#include <QDebug>
#include <QThread>
#include <QThreadPool>

class FunctionAnalyzer
{
public:
  FunctionAnalyzer(){}
  map<QString, FixedClass> findOriginalClass(map<QString, FixedClass> *classes);
  FixedClass findOriginalClass(QString cls, map<QString, FixedClass> *classes);
  map<QString, QStringList> addUsedClassImports(map<QString, FixedClass> *classes, vector<RawClass> *rawClasses);
  QStringList addUsedClassImports(QString cls, map<QString, FixedClass> *classes, vector<RawClass> *rawClasses);
  void addUsedCLassImportsHelper(QStringList *includes, map<QString, FixedClass> *classes, QString line, bool sec = false);
};

class FunctionAnalyzerTask : public QRunnable
{
private:
  uint offset, length;
  FunctionAnalyzer* funcAnalyzer;
  vector<RawClass> *rawClasses;
  map<QString, FixedClass> *classes;
  map<QString, QStringList> *includes;

public:
  FunctionAnalyzerTask(FunctionAnalyzer* funcAnalyzer, map<QString, QStringList>* includes, map<QString, FixedClass> *classes, vector<RawClass> *rawClasses, uint offset, uint length)
  {
    this->includes = includes;
    this->funcAnalyzer = funcAnalyzer;
    this->classes = classes;
    this->rawClasses = rawClasses;
    this->offset = offset;
    this->length = length;
  }

  void run() override
  {
      auto it = classes->begin();
      std::advance(it, offset);
      for (uint i = offset; i < length; i++) {
#if DEBUGMODE
          cout << "Add Used Class Imports " << it->first.toStdString().c_str();
#endif

          includes->insert_or_assign(it->first, funcAnalyzer->addUsedClassImports(it->first, classes, rawClasses));
          if (i < classes->size() - 1)
              std::advance(it, 1);

#if DEBUGMODE
          cout << "DONE" << endl;
#endif
      }
  }
};

#endif // FUNCTIONANALYZER_H
