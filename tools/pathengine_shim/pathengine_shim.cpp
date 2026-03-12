// pathengine_shim.cpp - PathEngine v5.01.01 preprocess generation pipeline
// Build (32-bit MinGW): see build.sh
//
// CONFIRMED v5.01.01 iMesh vtable indices:
//   [34] = saveGround(format, includeMapping, ostream)
//   [43] = generateUnobstructedSpaceFor(shape, options) [ret 8]
//   [44] = generatePathfindPreprocessFor(shape, options) [ret 8]
//   [45] = releaseUnobstructedSpaceFor(shape) [ret 4]
//   [46] = releasePathfindPreprocessFor(shape) [ret 4]
//   [47] = preprocessGenerationCompleted() [ret]
//   [48] = shapeCanCollide(shape) [ret 4]
//   [49] = shapeCanPathfind(shape) [ret 4]
//   [52] = saveUnobstructedSpaceFor(shape, ostream) - must be before PGC
//   [53] = savePathfindPreprocessFor(shape, ostream) - must be before PGC
//
// Pipeline: genUO[43] -> genPP[44] -> saveGround[34] -> saveUO[52] -> savePP[53] -> PGC[47]

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <windows.h>

typedef long tSigned32;
typedef unsigned long tUnsigned32;

struct ErrorHandler { void** vtbl; };
static int g_errorCount = 0;
static tSigned32 __attribute__((thiscall))
errHandler_handle(ErrorHandler*, const char* type, const char* desc,
                  const char* const* attrs) {
    g_errorCount++;
    fprintf(stderr, "  PE [%s]: %s\n", type ? type : "?", desc ? desc : "?");
    fflush(stderr);
    return 0;
}
static void __attribute__((thiscall)) errHandler_dtor(ErrorHandler*) {}
static void* g_errHandlerVtbl[] = { (void*)errHandler_dtor, (void*)errHandler_handle };

struct OutputStream {
    void** vtbl;
    char* data; tUnsigned32 size; tUnsigned32 capacity;
};
static void __attribute__((thiscall))
outStream_put(OutputStream* self, const char* d, tUnsigned32 s) {
    if (self->size + s > self->capacity) {
        self->capacity = (self->size + s) * 2;
        if (self->capacity < 4096) self->capacity = 4096;
        self->data = (char*)realloc(self->data, self->capacity);
    }
    memcpy(self->data + self->size, d, s);
    self->size += s;
}
static void __attribute__((thiscall)) outStream_dtor(OutputStream*) {}
static void* g_outStreamVtbl[] = { (void*)outStream_dtor, (void*)outStream_put };
static void outStream_init(OutputStream* os) {
    os->vtbl = g_outStreamVtbl; os->data = nullptr; os->size = 0; os->capacity = 0;
}
static void outStream_free(OutputStream* os) {
    free(os->data); os->data = nullptr; os->size = os->capacity = 0;
}

struct FaceVertexMesh {
    void** vtbl;
    tSigned32 numFaces, numVerts;
    tSigned32 *indices, *vx, *vy;
    float *vz;
};
static void __attribute__((thiscall)) fvm_dtor(FaceVertexMesh*) {}
static tSigned32 __attribute__((thiscall)) fvm_faces(const FaceVertexMesh* s) { return s->numFaces; }
static tSigned32 __attribute__((thiscall)) fvm_vertices(const FaceVertexMesh* s) { return s->numVerts; }
static tSigned32 __attribute__((thiscall)) fvm_vertexIndex(const FaceVertexMesh* s, tSigned32 f, tSigned32 v) { return s->indices[f*3+v]; }
static tSigned32 __attribute__((thiscall)) fvm_vertexX(const FaceVertexMesh* s, tSigned32 i) { return s->vx[i]; }
static tSigned32 __attribute__((thiscall)) fvm_vertexY(const FaceVertexMesh* s, tSigned32 i) { return s->vy[i]; }
static float __attribute__((thiscall)) fvm_vertexZ(const FaceVertexMesh* s, tSigned32 i) { return s->vz[i]; }
static tSigned32 __attribute__((thiscall)) fvm_faceAttr(const FaceVertexMesh*, tSigned32, tSigned32 a) { return (a == 1) ? 0 : -1; }
static void* g_fvmVtbl[] = {
    (void*)fvm_dtor, (void*)fvm_faces, (void*)fvm_vertices,
    (void*)fvm_vertexIndex, (void*)fvm_vertexX, (void*)fvm_vertexY,
    (void*)fvm_vertexZ, (void*)fvm_faceAttr
};

typedef void* (__stdcall *GetIPathEngineFn)(void*);

// iMesh vtable function types
typedef void  (__attribute__((thiscall)) *DestroyFn)(void*);
typedef void  (__attribute__((thiscall)) *GenUOFn)(void*, void*, const char*const*);     // [43]
typedef void  (__attribute__((thiscall)) *GenPPFn)(void*, void*, const char*const*);     // [44]
typedef void  (__attribute__((thiscall)) *PGCFn)(void*);                                  // [47]
typedef int   (__attribute__((thiscall)) *BoolShapeFn)(void*, void*);                     // [48],[49]
typedef void  (__attribute__((thiscall)) *SaveGroundFn)(void*, const char*, int, void*);  // [34]
typedef void  (__attribute__((thiscall)) *SaveShapeFn)(void*, void*, void*);              // [52],[53]

static tSigned32 g_testVx[] = {0, 1000, 1000, 0};
static tSigned32 g_testVy[] = {0, 0, 1000, 1000};
static float     g_testVz[] = {0.f, 0.f, 0.f, 0.f};
static tSigned32 g_testIdx[] = {0,3,2, 0,2,1};

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    const char* dll_path = "C:/Program Files (x86)/Steam/steamapps/common"
                           "/Titan Quest Anniversary Edition/pathengine.dll";
    HMODULE hDll = LoadLibraryA(dll_path);
    if (!hDll) { printf("LoadLibrary FAILED err=%lu\n", GetLastError()); return 1; }

    auto getIPE = (GetIPathEngineFn)GetProcAddress(hDll, "_DllExport_GetIPathEngine@4");
    ErrorHandler errHandler = {g_errHandlerVtbl};
    void* pe = getIPE(&errHandler);

    typedef tSigned32 (__attribute__((thiscall)) *IntFn)(void*);
    printf("PathEngine v%ld.%ld\n\n",
           ((IntFn)(*(void***)pe)[1])(pe),
           ((IntFn)(*(void***)pe)[2])(pe));

    // Build test mesh (2 triangles, 1000x1000 square)
    FaceVertexMesh fvm = {g_fvmVtbl, 2, 4, g_testIdx, g_testVx, g_testVy, g_testVz};
    void* fvmPtrs[] = {&fvm};
    typedef void* (__attribute__((thiscall)) *BuildMeshFn)(void*, void**, tUnsigned32, const char*const*);
    void* mesh = ((BuildMeshFn)(*(void***)pe)[10])(pe, fvmPtrs, 1, nullptr);
    printf("mesh = %p\n", mesh);

    // Create shape (20-unit square)
    tSigned32 sc[] = {20, -20, -20, -20, -20, 20, 20, 20};
    typedef void* (__attribute__((thiscall)) *NewShapeFn)(void*, tUnsigned32, const tSigned32*);
    void* shape = ((NewShapeFn)(*(void***)pe)[8])(pe, 4, sc);
    printf("shape = %p\n", shape);

    void** vt = *(void***)mesh;

    // ============================================================
    // Step 1: generateUnobstructedSpaceFor [43]
    // ============================================================
    printf("\n1. genUO [43]... ");
    g_errorCount = 0;
    ((GenUOFn)vt[43])(mesh, shape, nullptr);
    printf("OK (errs=%d) canCollide=%d\n", g_errorCount,
           ((BoolShapeFn)vt[48])(mesh, shape));

    // ============================================================
    // Step 2: generatePathfindPreprocessFor [44]
    // ============================================================
    printf("2. genPP [44]... ");
    g_errorCount = 0;
    ((GenPPFn)vt[44])(mesh, shape, nullptr);
    printf("OK (errs=%d)\n", g_errorCount);

    // ============================================================
    // Step 3: Save everything (BEFORE PGC!)
    // ============================================================
    OutputStream osGround, osCollision, osPathfind;

    printf("3. saveGround [34]... ");
    outStream_init(&osGround);
    g_errorCount = 0;
    ((SaveGroundFn)vt[34])(mesh, "tok", 1, &osGround);
    printf("%lu bytes (errs=%d)\n", osGround.size, g_errorCount);

    printf("   saveCollisionPreprocess [52]... ");
    outStream_init(&osCollision);
    g_errorCount = 0;
    ((SaveShapeFn)vt[52])(mesh, shape, &osCollision);
    printf("%lu bytes (errs=%d)\n", osCollision.size, g_errorCount);

    printf("   savePathfindPreprocess [53]... ");
    outStream_init(&osPathfind);
    g_errorCount = 0;
    ((SaveShapeFn)vt[53])(mesh, shape, &osPathfind);
    printf("%lu bytes (errs=%d)\n", osPathfind.size, g_errorCount);

    // ============================================================
    // Step 4: preprocessGenerationCompleted [47]
    // ============================================================
    printf("4. PGC [47]... ");
    ((PGCFn)vt[47])(mesh);
    printf("OK canCollide=%d canPathfind=%d\n",
           ((BoolShapeFn)vt[48])(mesh, shape),
           ((BoolShapeFn)vt[49])(mesh, shape));

    // ============================================================
    // Write output files
    // ============================================================
    if (osGround.size > 0) {
        FILE* f = fopen("test_ground.tok", "wb");
        if (f) { fwrite(osGround.data, 1, osGround.size, f); fclose(f); }
        printf("\n-> test_ground.tok (%lu bytes)\n", osGround.size);
    }
    if (osCollision.size > 0) {
        FILE* f = fopen("test_collision.tok", "wb");
        if (f) { fwrite(osCollision.data, 1, osCollision.size, f); fclose(f); }
        printf("-> test_collision.tok (%lu bytes)\n", osCollision.size);
    }
    if (osPathfind.size > 0) {
        FILE* f = fopen("test_pathfind.tok", "wb");
        if (f) { fwrite(osPathfind.data, 1, osPathfind.size, f); fclose(f); }
        printf("-> test_pathfind.tok (%lu bytes)\n", osPathfind.size);
    }

    outStream_free(&osGround);
    outStream_free(&osCollision);
    outStream_free(&osPathfind);

    // Clean up
    ((DestroyFn)vt[0])(mesh);

    FreeLibrary(hDll);
    printf("\n=== Done ===\n");
    return 0;
}
