#include <iostream>

#include <QCoreApplication>
#include <QElapsedTimer>
#include <QString>

#include "classner.h"
#include "rawclass.h"
#include "structer.h"
#include "classstorer.h"
#include "classreader.h"
#include "reinterpretalter.h"
#include "functionanalyzer.h"
#include "classanalyzer.h"
#include "gotogo.h"

using namespace std;


static bool skipClassWrite = false;
static bool skipReinterpret = false;
static bool skipAnalyze = false;
static bool skipRemoveIncluded = false;
static bool skipClassAnalyze = false;


static bool argumentExists(char* arg, const char* search)
{
  return QString::fromLocal8Bit((const char*)arg, strlen(arg)) == QString(search);
}

static void printElapsedTime(QElapsedTimer *elapsedTimer)
{
  ulong msecs = elapsedTimer->elapsed();
  ulong secs = msecs / 1000;
  if ((msecs % 1000) > 0) secs++;
  ulong hours = secs / 3600;
  secs = secs % 3600;
  ulong mins = secs / 60;
  secs = secs % 60;
  cout << "Time taken: " << hours << ":" << mins << ":" << secs << endl;
}

static void printSkipOptions()
{
  // print options
  cout << "SkipClassWrite: " << ((skipClassWrite) ? "True" : "False") << endl;
  cout << "SkipReinterpret: " << ((skipReinterpret) ? "True" : "False") << endl;
  cout << "SkipAnalyze: " << ((skipAnalyze) ? "True" : "False") << endl;
  cout << "SkipRemoveIncluded: " << ((skipRemoveIncluded) ? "True" : "False") << endl;
  cout << "SkipClassAnalyze: " << ((skipClassAnalyze) ? "True" : "False") << endl;
}

static void DownDir(QDir dir, QStringList* listX)
{
  const QFileInfoList list = dir.entryInfoList();
  QFileInfo fi;
  for (int l = 0; l < list.size(); l++)
  {
      fi = list.at(l);
      if (fi.isDir() && fi.fileName() != "." && fi.fileName() != "..")
      {
          DownDir(fi.absoluteFilePath(), listX);
      }
      else if (fi.isFile() && fi.path().endsWith(".h"))
      {
          listX->append(fi.absoluteFilePath());
      }
  }
}

static void removeIncluded(QString moduleDir, QString moduleName, QString operatingDir = "./generated_classes")
{
  bool standardDir = true;
  QString originalDir = QDir::currentPath();
  if (operatingDir != ".") {
      standardDir = false;
      operatingDir = operatingDir.replace('/', QDir::separator());
      QDir::setCurrent(operatingDir);
  }

  moduleDir = moduleDir.replace("/", QDir::separator());

  QStringList files;
  QDir glob(moduleDir);
  DownDir(glob, &files);

  QStringList excludedDirs;
  excludedDirs.append(".git");

  QStringList fileNames;
  foreach (QString filePath, files) {
      bool foundExl = false;
      foreach (QString dirPath, excludedDirs) {
          if (filePath.contains(dirPath + QDir::separator()) || filePath.endsWith(dirPath) || filePath.startsWith(dirPath)) {
              foundExl = true;
              break;
          }
      }

      if (!foundExl) {
          fileNames.append(filePath.split(QDir::separator()).last());
      }
  }

  QString sourceFile;
  QStringList fileNamesFound;
  foreach (QString headerFile, fileNames) {
      if (QFile::exists(headerFile) && QFileInfo(headerFile).isFile()) {
          if (QFile::remove(headerFile)) {
              fileNamesFound.append(headerFile);
          }
      }

      sourceFile = headerFile.replace(".h", ".cpp");
      if (QFile::exists(sourceFile) && QFileInfo(sourceFile).isFile()) {
          QFile::remove(sourceFile);
      }
  }

  map<QString, QString> cortess;
  QString fileName, filex2;
  foreach (QString filex, files) {
      fileName = filex.split(QDir::separator()).last();
      if (fileNamesFound.contains(fileName)) {
          filex2 = filex.mid(filex.indexOf(moduleName)).replace(moduleName, moduleDir);
          cortess.insert_or_assign(fileName, filex2);
      }
  }

  QStringList allMyFiles = QDir(".").entryList(QDir::Files | QDir::NoDotAndDotDot);
  foreach (QString file, allMyFiles) {
      if (file.endsWith(".h")) {
          QFile f(file);
          if (!f.open(QFile::ReadOnly | QFile::Text))
          {
              cout << "ERROR1 file read removeIncludes: " << file.toStdString().c_str() << endl;
              continue;
          }
          QTextStream in(&f);
          QString alla = in.readAll();
          foreach (auto incl, cortess) {
              alla = alla.replace("\"" + incl.first + "\"", "\"" + incl.second + "\"");
          }
          f.close();
          QFile f2(file);
          if (!f2.open(QFile::WriteOnly | QFile::Text))
          {
              cout << "ERROR2 file read removeIncludes: " << file.toStdString().c_str() << endl;
              continue;
          }
          QTextStream out(&f2);
          out << alla;
          f2.close();
      }
  }

  // finish up and reset to original working dir
  if (!standardDir) {
    QDir::setCurrent(originalDir);
  }
}


int main(int argc, char *argv[])
{
  QCoreApplication a(argc, argv);

  QString filePath = "";

  if (argc > 0) {
      filePath = argv[1];
      if (argc > 1) {
          for (int i = 1; i < argc; i++) {
              if (argumentExists(argv[i], "-sc"))
                  skipClassWrite = true;
              else if (argumentExists(argv[i], "-sr"))
                  skipReinterpret = true;
              else if (argumentExists(argv[i], "-sa"))
                  skipAnalyze = true;
              else if (argumentExists(argv[i], "-si"))
                  skipRemoveIncluded = true;
              else if (argumentExists(argv[i], "-sa2"))
                  skipClassAnalyze = true;
              else if (argumentExists(argv[i], "--skip-all")){
                  skipClassWrite = true;
                  skipReinterpret = true;
                  skipAnalyze = true;
                  skipRemoveIncluded = true;
                  skipClassAnalyze = true;
              }
          }
      }
  }

  printSkipOptions();


  if (filePath.isEmpty()) {
      cout << "No file given!" << endl;
      return 1;
  }


  // Start program time watch
  QElapsedTimer elapsedTimer;
  elapsedTimer.start();


  cout << "Processing cpp file ..." << endl;

  ClassStorer::initValues();

  Structer structer;
  structer.readStructs(filePath);

  Classner classner;
  classner.readClassFunctions(filePath, skipClassWrite);
  vector<RawClass> classes = classner.getClasses();

  ClassStorer classStorer(structer, classes);

  if (!skipClassWrite) {
    classStorer.writeClasses();
    classStorer.updateNewCppFile(filePath/*, classes*/);
  }

  if (!skipReinterpret) {
    ReinterpretAlter reinterpret;
    reinterpret.removeReinterpret(classes);
  }

  ClassReader classReader;
  classReader.readClasses();
  map<QString, FixedClass> modifiedClasses = classReader.getClasses();

  // remove default cpp file from class check - change later with different behavior
  QStringList pathArray = filePath.split("/");
  QString fileName = pathArray.back().split(".")[0];
  modifiedClasses.erase(fileName);

  map<QString, FixedClass> bakModClasses;
  foreach (auto c, modifiedClasses) {
      bakModClasses.insert_or_assign(c.first, c.second);
  }

  if (!skipAnalyze) {
      FunctionAnalyzer funcAnalyzer;
      map<QString, FixedClass> fixedClasses = funcAnalyzer.findOriginalClass(&modifiedClasses);
      map<QString, QStringList> classIncludes = funcAnalyzer.addUsedClassImports(&fixedClasses, &classes); // FIXME: bottleneck!!!
      // fixed_classes = analyzer.removeInvalidParams(fixed_classes, classes) # FIXME: broken at the moment
      classStorer.writeClassesJust(fixedClasses, classIncludes);
  }

  if (!skipRemoveIncluded) {
      cout << "Remove included..." << endl;
      removeIncluded(QString("../warband_mangled_source/havok-2013").replace("/", QDir::separator()), "havok-2013"); // example with Havok-2013
  }

  if (!skipClassAnalyze) {
      cout << "Class Analyzing..." << endl;
      ClassAnalyzer classAnalyzer;
      classAnalyzer.findClassAttributes(&bakModClasses); // FIXME: only works when previous are done and skipped second run
      // TODO: later retrieve actual attributes maybe and then store in actual class files etc.
      // - - -
      GoToGo gotogo;
      gotogo.processClasses(&modifiedClasses);

      QStringList files = QDir(".").entryList(QDir::Files | QDir::NoDotAndDotDot);
      foreach (QString file, files) {
          if (file.contains("_") && file.endsWith(".cpp")) {
              QFile fx(file);
              fx.copy(QString("./endl/class_info/" + file).replace("/", QDir::separator()));
              fx.remove();
          }
      }
  }


  // Stop program time watch
  printElapsedTime(&elapsedTimer);
  elapsedTimer.invalidate();

  return 0;
}
