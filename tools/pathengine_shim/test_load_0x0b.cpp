// test_load_0x0b.cpp - Test loading real TQAE 0x0b body with PathEngine
// Confirmed: loadMeshFromBuffer is at iPathEngine vtable[7] in v5.01.01
// Build: /c/msys64/mingw32/bin/g++.exe -o test_load_0x0b.exe test_load_0x0b.cpp -static-libgcc -static-libstdc++ -Wall -Wno-attributes -O2

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
                  const char* const*) {
    g_errorCount++;
    fprintf(stderr, "  PE [%s]: %s\n", type ? type : "?", desc ? desc : "?");
    fflush(stderr);
    return 0;
}
static void __attribute__((thiscall)) errHandler_dtor(ErrorHandler*) {}
static void* g_errHandlerVtbl[] = { (void*)errHandler_dtor, (void*)errHandler_handle };

struct OutputStream { void** vtbl; char* data; tUnsigned32 size; tUnsigned32 capacity; };
static void __attribute__((thiscall))
os_put(OutputStream* self, const char* d, tUnsigned32 s) {
    if (self->size + s > self->capacity) {
        self->capacity = (self->size + s) * 2;
        if (self->capacity < 4096) self->capacity = 4096;
        self->data = (char*)realloc(self->data, self->capacity);
    }
    memcpy(self->data + self->size, d, s);
    self->size += s;
}
static void __attribute__((thiscall)) os_dtor(OutputStream*) {}
static void* g_osVtbl[] = { (void*)os_dtor, (void*)os_put };

struct FVM { void** vtbl; tSigned32 nf, nv; tSigned32 *idx, *vx, *vy; float *vz; };
static void __attribute__((thiscall)) fvm_d(FVM*) {}
static tSigned32 __attribute__((thiscall)) fvm_f(const FVM* s) { return s->nf; }
static tSigned32 __attribute__((thiscall)) fvm_v(const FVM* s) { return s->nv; }
static tSigned32 __attribute__((thiscall)) fvm_vi(const FVM* s, tSigned32 f, tSigned32 v) { return s->idx[f*3+v]; }
static tSigned32 __attribute__((thiscall)) fvm_vx(const FVM* s, tSigned32 i) { return s->vx[i]; }
static tSigned32 __attribute__((thiscall)) fvm_vy(const FVM* s, tSigned32 i) { return s->vy[i]; }
static float __attribute__((thiscall)) fvm_vz(const FVM* s, tSigned32 i) { return s->vz[i]; }
static tSigned32 __attribute__((thiscall)) fvm_fa(const FVM*, tSigned32, tSigned32 a) { return (a==1)?0:-1; }
static void* g_fvmVtbl[] = {(void*)fvm_d,(void*)fvm_f,(void*)fvm_v,(void*)fvm_vi,(void*)fvm_vx,(void*)fvm_vy,(void*)fvm_vz,(void*)fvm_fa};

typedef void* (__stdcall *GetIPathEngineFn)(void*);
typedef tSigned32 (__attribute__((thiscall)) *IntFn)(void*);
typedef void* (__attribute__((thiscall)) *LoadMeshFn)(void*, const char*, const char*, tUnsigned32, const char*const*);
typedef void (__attribute__((thiscall)) *DestroyFn)(void*);
typedef void* (__attribute__((thiscall)) *BuildMeshFn)(void*, void**, tUnsigned32, const char*const*);
typedef void (__attribute__((thiscall)) *SaveGroundFn)(void*, const char*, int, void*);

static char* read_file(const char* path, tUnsigned32* out_size) {
    FILE* f = fopen(path, "rb");
    if (!f) return nullptr;
    fseek(f, 0, SEEK_END);
    *out_size = (tUnsigned32)ftell(f);
    fseek(f, 0, SEEK_SET);
    char* buf = (char*)malloc(*out_size);
    fread(buf, 1, *out_size, f);
    fclose(f);
    return buf;
}

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    HMODULE hDll = LoadLibraryA("C:/Program Files (x86)/Steam/steamapps/common"
                                "/Titan Quest Anniversary Edition/pathengine.dll");
    if (!hDll) { printf("LoadLibrary FAILED err=%lu\n", GetLastError()); return 1; }

    auto getIPE = (GetIPathEngineFn)GetProcAddress(hDll, "_DllExport_GetIPathEngine@4");
    ErrorHandler errHandler = {g_errHandlerVtbl};
    void* pe = getIPE(&errHandler);
    void** peVt = *(void***)pe;

    printf("PathEngine interface v%ld.%ld\n\n",
           ((IntFn)peVt[1])(pe), ((IntFn)peVt[2])(pe));

    // v18 has loadMeshFromBuffer at [10], v5.01.01 shifts -1 = [9]
    // ([7] = shapeIsValid, [8] = newShape, [9] = loadMeshFromBuffer, [10] = buildMeshFromContent)
    auto loadMesh = (LoadMeshFn)peVt[9];

    // === Test 1: Round-trip our own tok mesh ===
    printf("=== Test 1: Round-trip tok mesh ===\n");
    tSigned32 tvx[] = {0,1000,1000,0}, tvy[] = {0,0,1000,1000}, tidx[] = {0,3,2, 0,2,1};
    float tvz[] = {0,0,0,0};
    FVM fvm = {g_fvmVtbl, 2, 4, tidx, tvx, tvy, tvz};
    void* fvmPtrs[] = {&fvm};
    void* testMesh = ((BuildMeshFn)peVt[10])(pe, fvmPtrs, 1, nullptr);
    printf("  Built mesh: %p\n", testMesh);

    OutputStream os = {g_osVtbl, nullptr, 0, 0};
    ((SaveGroundFn)(*(void***)testMesh)[34])(testMesh, "tok", 1, &os);
    printf("  Saved tok: %lu bytes\n", os.size);

    // Save tok to file for analysis
    FILE* tf = fopen("test_ground.tok", "wb");
    if (tf) { fwrite(os.data, 1, os.size, tf); fclose(tf); }

    ((DestroyFn)(*(void***)testMesh)[0])(testMesh);

    g_errorCount = 0;
    void* reloaded = loadMesh(pe, "tok", os.data, os.size, nullptr);
    printf("  Reloaded: %p (errs=%d)\n", reloaded, g_errorCount);
    if (reloaded) {
        // Validate: try getting mesh vtable and calling a safe method
        void** mvt = *(void***)reloaded;
        // vtable[48] = shapeCanCollide should be safe to call concept
        printf("  vtable=%p\n", (void*)mvt);
        ((DestroyFn)mvt[0])(reloaded);
        printf("  Round-trip PASSED!\n");
    }
    free(os.data);

    // === Test 2: Load real 0x0b body with various format strings ===
    printf("\n=== Test 2: Load real 0x0b body ===\n");

    tUnsigned32 body_size = 0, full_size = 0;
    char* body = read_file("C:/Users/willi/repos/tqit_soulvizier_classic/local/pathengine_analysis/rec02_body.bin", &body_size);
    char* full = read_file("C:/Users/willi/repos/tqit_soulvizier_classic/local/pathengine_analysis/rec02_full.bin", &full_size);
    if (!body || !full) { printf("Failed to read input files\n"); return 1; }
    printf("  Body: %lu bytes, Full section: %lu bytes\n\n", body_size, full_size);

    struct { const char* fmt; const char* data; tUnsigned32 size; const char* desc; } tests[] = {
        {"tok", body, body_size,          "body as tok"},
        {"xml", body, body_size,          "body as xml"},
        {"tok", body+60, body_size-60,    "from RLTD offset 60"},
        {"tok", body+44, body_size-44,    "from offset 44"},
        {"tok", full, full_size,          "full REC\\x02 section"},
        {"tok", full+4, full_size-4,      "section from offset 4"},
        {nullptr, nullptr, 0, nullptr}
    };

    for (int i = 0; tests[i].desc; i++) {
        printf("  [%d] fmt=\"%s\" %s (%lu bytes)... ",
               i, tests[i].fmt, tests[i].desc, tests[i].size);
        fflush(stdout);
        g_errorCount = 0;
        void* m = loadMesh(pe, tests[i].fmt, tests[i].data, tests[i].size, nullptr);
        if (m) {
            printf("LOADED! mesh=%p (errs=%d)\n", m, g_errorCount);
            ((DestroyFn)(*(void***)m)[0])(m);
        } else {
            printf("NULL (errs=%d)\n", g_errorCount);
        }
    }

    // === Test 3: Load 0x0a (PTH\x04) tok data ===
    printf("\n=== Test 3: Load PTH tok data from 0x0a section ===\n");
    tUnsigned32 pth_size = 0;
    char* pth_data = read_file("C:/Users/willi/repos/tqit_soulvizier_classic/local/pathengine_analysis/pth04_clean_tok.bin", &pth_size);
    if (pth_data) {
        printf("  PTH tok: %lu bytes, starts with: ", pth_size);
        for (unsigned i = 0; i < 16 && i < pth_size; i++) printf("%02x ", (unsigned char)pth_data[i]);
        printf("\n");

        g_errorCount = 0;
        void* pthMesh = loadMesh(pe, "tok", pth_data, pth_size, nullptr);
        if (pthMesh) {
            printf("  LOADED! mesh=%p (errs=%d) -- PTH tok data IS compatible with v5!\n", pthMesh, g_errorCount);
            ((DestroyFn)(*(void***)pthMesh)[0])(pthMesh);
        } else {
            printf("  NULL (errs=%d) -- PTH tok data NOT compatible\n", g_errorCount);
        }
        free(pth_data);
    } else {
        printf("  Could not read pth04_clean_tok.bin\n");
    }

    free(body);
    free(full);
    FreeLibrary(hDll);
    printf("\n=== Done ===\n");
    return 0;
}
