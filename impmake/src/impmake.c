/*
 *  Copyright (c) 2008 by the people mentioned in the file AUTHORS.
 *
 *  This software is licensed under the terms mentioned in the file LICENSE.
 */

#include "version.h"
#include "disphelper.h"
#include <stdio.h>
#include <ctype.h>
#include <unistd.h>
#include <wchar.h>
#include <tchar.h>
#include <time.h>
#include <getopt.h>

#define COM_TRY(func) if (FAILED(func)) { \
                      char szMessage[512]; \
                      dhFormatExceptionA(NULL, szMessage, sizeof(szMessage)/sizeof(szMessage[0]), TRUE); \
                      printf("\nExecution failed at %s:%d while attempting to execute\n  %s\n\n%s\n", \
                      __FILE__, __LINE__, #func, szMessage); result = 2; goto cleanup; }

#define STRTRIM(str)   { int n = strlen(str); \
                         while(n > 0 && isspace(str[--n])) str[n] = 0; }
#define SET_OPT(target) { strncpy(target, optarg, (sizeof(target)/sizeof(char))-1);\
                          target[(sizeof(target)/sizeof(char))-1] = 0; STRTRIM(target) }
#define TO_BOOL(i) ( (i == 0) ? FALSE : TRUE )
#define ABSPATH(p) _fullpath(pathspec, (p), sizeof(pathspec)/sizeof(char))

/* ============================================================================ */

static char author[256],  title   [256],  category [256], name    [256];
static char isbn  [256],  pubdate [256],  publisher[256], language[256];
static char outdir[1024], prj_save[1024], pathspec[1024], from   [1024];

static int device    = 0, zoom       = 2, help        = 0;
static int underline = 1, image_conv = 1, image_scale = 1;
static int compress  = 0, anchors    = 0, error_log   = 0;

static struct option long_options[] = {
    /* flags */
    {"no-underline", no_argument, &underline,   0},
    {"no-img-conv",  no_argument, &image_conv,  0},
    {"no-img-scale", no_argument, &image_scale, 0},
    {"compress",     no_argument, &compress,    1},
    {"keep-anchors", no_argument, &anchors,     1},
    {"oeb",          no_argument, &device,      0},
    {"1200",         no_argument, &device,      1},
    {"1150",         no_argument, &device,      2},
    {"1100",         no_argument, &device,      3},
    {"zoom-small",   no_argument, &zoom,        0},
    {"zoom-large",   no_argument, &zoom,        1},
    {"zoom-both",    no_argument, &zoom,        2},
    {"help",         no_argument, &help,        1},
    {"log",          no_argument, &error_log,   1},

    /* options */
    {"save",      required_argument, 0, 's' },
    {"author",    required_argument, 0, 'a' },
    {"title",     required_argument, 0, 't' },
    {"category",  required_argument, 0, 'c' },
    {"out-dir",   required_argument, 0, 'd' },
    {"name",      required_argument, 0, 'n' },
    {"isbn",      required_argument, 0, 'i' },
    {"pubdate",   required_argument, 0, 'u' },
    {"publisher", required_argument, 0, 'p' },
    {"language",  required_argument, 0, 'e' },
    {"from",      required_argument, 0, 'f' },

    /* end of options */
    {0, 0, 0, 0}
};

/* ============================================================================ */

void usage()
{
    printf("\n\
Usage: impmake [-OPTIONS] FILES [...]\n\n\
-v             Show the version.\n\
-h, --help     Show this help message.\n\n\
--1100, --1150, --1200, --oeb\n\
               Specify the target device to use for book creation.\n\
-f, --from     Specify a file containing list of HTML files.\n\
-d, --out-dir  Specify the output directory.\n\
-n, --name     Specify the book name.\n\
-a, --author   Specify the book's author.\n\
-t, --title    Specify the book's title.\n\
-c, --category Specify the book's category.\n\
-l, --log      Specify that an error log should be generated.\n\
-s, --save     Specify the project to save as.\n\
--isbn         Specify the book's ISBN\n\
--pubdate      Specify the book's publishing date\n\
--publisher    Specify the book's publisher\n\
--language     Specify the language for the book.\n\
--zoom-small, --zoom-large, --zoom-both\n\
               Specify the zoom states to be supported in the book\n\n\
--no-underline Specify that links should not be underlined.\n\
--no-img-conv  Specify that image auto conversion to JPG should be disabled.\n\
--no-img-scale Specify that image pre scaling should be disabled.\n\
--compress     Specify that the compression is to be used.\n\
--keep-anchors Specify that link anchors should be kept in output.\n");
    exit(0);
}

void load_options(int argc, char ** argv)
{
    time_t current;
    int c, index = 0, error = 0;

    /* set default option values */
    current = time(NULL);
    strcpy(author,   "Unknown");
    strcpy(title,    asctime(localtime(&current))); STRTRIM(title);
    strcpy(category, "Unclassified");
    strcpy(name,     "ebook");
    strcpy(outdir,   ".");
    strcpy(isbn,     "");  strcpy(pubdate,  "");  strcpy(publisher, "");
    strcpy(language, "");  strcpy(prj_save, "");  strcpy(from,      "");

    /* parse options */
    while(1)
    {
        c = getopt_long(argc, argv, "hvls:a:t:c:d:n:f:",
                        long_options, &index);
        if (c == EOF)
            break;

        switch(c)
        {
            case 0  :  break;
            case 's':  SET_OPT(prj_save);  break;
            case 'a':  SET_OPT(author);    break;
            case 't':  SET_OPT(title);     break;
            case 'c':  SET_OPT(category);  break;
            case 'd':  SET_OPT(outdir);    break;
            case 'n':  SET_OPT(name);      break;
            case 'i':  SET_OPT(isbn);      break;
            case 'u':  SET_OPT(pubdate);   break;
            case 'p':  SET_OPT(publisher); break;
            case 'e':  SET_OPT(language);  break;
            case 'f':  SET_OPT(from);      break;
            case 'l':  error_log = 1;      break;
            case 'v':  printf("impmake %s\n", VERSION); exit(0);
            default:   error     = 1;      break;
       }
    }

    if(error)
    {
        fprintf(stderr, "\nType %s --help for usage.\n", argv[0]);
        exit(1);
    }

    if(help)
        usage();

    if(from[0] && ABSPATH(from))
        strcpy(from, pathspec);

    if(ABSPATH(outdir))
        strcpy(outdir, pathspec);
}

int build_imp(int argc, char **argv)
{
    int result = 0, count = 0;
    FILE *from_list;
    char src_file[1024];

    DISPATCH_OBJ(impProject);
    DISPATCH_OBJ(impBuilder);

    COM_TRY( dhCreateObject(L"SBPublisher.Project", NULL, &impProject) );
    COM_TRY( dhCreateObject(L"SBPublisher.Builder", NULL, &impBuilder) );

    COM_TRY( dhCallMethod(impProject, L".ClearAll()") );

    if(from[0] && !access(from, R_OK) && (from_list = fopen(from, "r")))
    {
        while( fgets(src_file, 1024, from_list) )
        {
            STRTRIM(src_file);
            if(src_file[0] && ABSPATH(src_file) && !access(pathspec, R_OK))
            {
                COM_TRY( dhCallMethod(impProject, L".AddSourceFile(%s)", src_file) );
                count++;
            }
        }
        fclose(from_list);
    }

    while (optind < argc)
    {
        if(ABSPATH(argv[optind++]) && !access(pathspec, R_OK))
        {
            COM_TRY( dhCallMethod(impProject, L".AddSourceFile(%s)", pathspec) );
            count++;
        }
    }

    if(count == 0)
    {
        fprintf(stderr, "No valid files were specified for creation, aborting.\n");
        result = 1;
        goto cleanup;
    }

    COM_TRY( dhPutValue(impProject, L".AuthorFirstName = %s", author)  );
    COM_TRY( dhPutValue(impProject, L".AuthorFileAs    = %s", author)  );
    COM_TRY( dhPutValue(impProject, L".BookTitle       = %s", title)   );
    COM_TRY( dhPutValue(impProject, L".Category        = %s", category));
    COM_TRY( dhPutValue(impProject, L".BookFileName    = %s", name)    );
    COM_TRY( dhPutValue(impProject, L".OutputDirectory = %s", outdir)  );

    if(error_log)
    {
        COM_TRY( dhPutValue(impProject, L".ErrorDirectory  = %s", outdir)  );
        COM_TRY( dhPutValue(impProject, L".ErrorFeedback   = %b", TRUE)    );
    }

    if(isbn[0])
        COM_TRY( dhPutValue(impProject, L".ISBN        = %s", isbn)      );
    if(publisher[0])
        COM_TRY( dhPutValue(impProject, L".Publisher   = %s", publisher) );
    if(pubdate[0])
        COM_TRY( dhPutValue(impProject, L".PublishDate = %s", pubdate)   );
    if(language[0])
        COM_TRY( dhPutValue(impProject, L".Language    = %s", language)  );

    COM_TRY( dhPutValue(impProject, L".Zoom            = %d", (long)zoom)           );
    COM_TRY( dhPutValue(impProject, L".Compress        = %b", TO_BOOL(compress))    );
    COM_TRY( dhPutValue(impProject, L".UnderlineLinks  = %b", TO_BOOL(underline))   );
    COM_TRY( dhPutValue(impProject, L".ConvertToJPEG   = %b", TO_BOOL(image_conv))  );
    COM_TRY( dhPutValue(impProject, L".PreScaleImages  = %b", TO_BOOL(image_scale)) );
    COM_TRY( dhPutValue(impProject, L".KeepAnchors     = %b", TO_BOOL(anchors))     );

    COM_TRY( dhPutValue(impProject, L".Encrypt         = %b", FALSE)   );
    COM_TRY( dhPutValue(impProject, L".RequireISBN     = %b", FALSE)   );
    COM_TRY( dhPutValue(impProject, L".BuildTarget = %d", (long)device) );

    COM_TRY( dhCallMethod(impBuilder, L".ValidateManifest(%o)", impProject) );

    if(prj_save[0])
    {
        if(ABSPATH(prj_save))
        {
            COM_TRY( dhCallMethod(impProject, L".Save(%s)", pathspec) );
        }
    }

    if(device == 0) {
        COM_TRY( dhCallMethod(impBuilder, L".GenerateOEBFF(%o, %b)", impProject, TRUE) );
    } else {
        COM_TRY( dhCallMethod(impBuilder, L".Build(%o)", impProject) );
    }

cleanup:
    SAFE_RELEASE(impProject);
    SAFE_RELEASE(impBuilder);

    return result;
}

/* ============================================================================ */

int main(int argc, char **argv)
{
    int result = 0;

    if(argc == 1)
        usage();
    load_options(argc, argv);

    dhInitialize(TRUE);
    result = build_imp(argc, argv);
    dhUninitialize(TRUE);

    exit(result);
}
