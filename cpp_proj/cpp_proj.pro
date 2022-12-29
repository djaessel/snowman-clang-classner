QT -= gui

CONFIG += c++17 console
CONFIG -= app_bundle

# You can make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

SOURCES += \
        classner.cpp \
        classreader.cpp \
        classstorer.cpp \
        fixedclass.cpp \
        fixedfunction.cpp \
        functionanalyzer.cpp \
        main.cpp \
        rawclass.cpp \
        rawfunction.cpp \
        reinterpretalter.cpp \
        structer.cpp

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

HEADERS += \
    classner.h \
    classreader.h \
    classstorer.h \
    fixedclass.h \
    fixedfunction.h \
    functionanalyzer.h \
    rawclass.h \
    rawfunction.h \
    reinterpretalter.h \
    specialvals.h \
    structer.h
