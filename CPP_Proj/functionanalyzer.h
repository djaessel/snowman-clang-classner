#ifndef FUNCTIONANALYZER_H
#define FUNCTIONANALYZER_H

#include <bits/stdc++.h>

#include "fixedclass.h"

class FunctionAnalyzer
{
public:
  FunctionAnalyzer();
  map<QString, FixedClass> findOriginalClass(map<QString, FixedClass> &classes);
  FixedClass findOriginalClass(QString cls, map<QString, FixedClass> &classes);
};

#endif // FUNCTIONANALYZER_H
