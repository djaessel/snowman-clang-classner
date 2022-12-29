#ifndef CLASSSTORER_H
#define CLASSSTORER_H

#include <QDir>
#include <QString>
#include <QTextStream>
#include <QStringList>

#include <bits/stdc++.h>
#include <iostream>

#include "specialvals.h"

#include "rawclass.h"
#include "structer.h"
#include "fixedclass.h"

using namespace std;


class ClassStorer
{
private:
  Structer structer;
  vector<RawClass> classList;

  map<QString, QString> allFuncs;
  map<QString, QString> allFuncClass;

  QString replaceSymbolsInLine(QString line);
  QString classFunctionParameterFix(QString fname, QString assemblyFuncName);

public:
  inline static QString ExportDir;
  inline static map<QString, QString> ParamTypes; // currently unused
  inline static QStringList ParamAsmNames;
  inline static map<QString, QString> Replaces;
  inline static QStringList AllValidTypes;
  inline static QStringList AllValidSpecialTypes;

  static void initValues();

  void writeClasses();
  void writeClassHeaderFile(RawClass cls);
  void writeClassCodeFile(RawClass cls);
  void writeStructsForHeader(RawClass cls);
  void updateNewCppFile(QString filePath/*, vector<RawClass> classes*/);
  void writeClassesJust(map<QString, FixedClass> fixedClasses, map<QString, QStringList> classIncludes);

  ClassStorer(Structer structer, vector<RawClass> classList);
};

#endif // CLASSSTORER_H
