#include <iostream>

#include <QCoreApplication>
#include <QString>

#include "classner.h"
#include "rawclass.h"
#include "classstorer.h"

using namespace std;

int main(int argc, char *argv[])
{
//  QCoreApplication a(argc, argv);

  bool skipClassWrite = false;
  bool skipReinterpret = false;
  bool skipAnalyze = false;
  bool skipRemoveIncluded = false;
  bool skipClassAnalyze = false;
  QString filePath = "";

  if (argc > 0) {
      filePath = argv[1];
      if (argc > 1) {
          for (int i = 1; i < argc; i++) {
              if (QString((const char*)argv[i]) == QString("-sc"))
                  skipClassWrite = true;
              if (QString::fromLocal8Bit((const char*)argv[i], strlen(argv[i])) == QString("-sr"))
                  skipReinterpret = true;
              if (QString::fromLocal8Bit((const char*)argv[i], strlen(argv[i])) == QString("-sa"))
                  skipAnalyze = true;
              if (QString::fromLocal8Bit((const char*)argv[i], strlen(argv[i])) == QString("-si"))
                  skipRemoveIncluded = true;
              if (QString::fromLocal8Bit((const char*)argv[i], strlen(argv[i])) == QString("-sa2"))
                  skipClassAnalyze = true;
              if (QString::fromLocal8Bit((const char*)argv[i], strlen(argv[i])) == QString("--skip-all")) {
                  skipClassWrite = true;
                  skipReinterpret = true;
                  skipAnalyze = true;
                  skipRemoveIncluded = true;
                  skipClassAnalyze = true;
              }
          }
      }
  }

  if (filePath.isEmpty()) {
      cout << "No file given!" << endl;
      return 1;
  }

  //stopwatch = Stopwatch()
  //stopwatch.start()

  cout << "Processing cpp file ..." << endl;

  //structer = Structer()
  //structer.readStructs(file_path)

  ClassStorer::initValues();

  Classner classner;
  classner.readClassFunctions(filePath, skipClassWrite);
  vector<RawClass> classes = classner.getClasses();

  ClassStorer classStorer(classes);
  classStorer.writeClasses();

//  return a.exec();
  return 0;
}
