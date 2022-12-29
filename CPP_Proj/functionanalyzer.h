#ifndef FUNCTIONANALYZER_H
#define FUNCTIONANALYZER_H

#include <bits/stdc++.h>

#include "specialvals.h"

#include "rawclass.h"
#include "fixedclass.h"

class FunctionAnalyzer
{
public:
  FunctionAnalyzer(){}
  map<QString, FixedClass> findOriginalClass(map<QString, FixedClass> &classes);
  FixedClass findOriginalClass(QString cls, map<QString, FixedClass> &classes);
  map<QString, QStringList> addUsedClassImports(map<QString, FixedClass> &classes, vector<RawClass> &rawClasses);
  QStringList addUsedClassImports(QString cls, map<QString, FixedClass> &classes, vector<RawClass> &rawClasses);
};

#endif // FUNCTIONANALYZER_H
