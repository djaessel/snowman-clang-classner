#ifndef CLASSSTORER_H
#define CLASSSTORER_H

#include <QDir>
#include <QString>
#include <QTextStream>
#include <QStringList>

#include <bits/stdc++.h>
#include <iostream>

#include "rawclass.h"
#include "structer.h"

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
  //void updateNewCppFile(QString filePath, vector<FixedClass> classes);
  //void writeClassesJust(vector<FixedClass> fixedClasses, QStringList classIncludes);
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
  void updateNewCppFile(QString filePath, vector<RawClass> classes);

  ClassStorer(Structer structer, vector<RawClass> classList);
};

#endif // CLASSSTORER_H
