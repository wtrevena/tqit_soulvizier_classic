#include <cstdio>
#include <windows.h>
typedef long tSigned32;
typedef unsigned long tUnsigned32;
struct ErrorHandler { void** vtbl; };
static tSigned32 __attribute__((thiscall))
errHandler_handle(ErrorHandler*, const char*, const char*, const char* const*) { return 0; }
static void __attribute__((thiscall)) errHandler_dtor(ErrorHandler*) {}
static void* g_errHandlerVtbl[] = { (void*)errHandler_dtor, (void*)errHandler_handle };

struct FVM { void** vtbl; tSigned32 nf, nv; tSigned32 *idx, *vx, *vy; float *vz; };
static void __attribute__((thiscall)) fvm_d(FVM*) {}
static tSigned32 __attribute__((thiscall)) fvm_f(const FVM* s) { return s->nf; }
static tSigned32 __attribute__((thiscall)) fvm_v(const FVM* s) { return s->nv; }
static tSigned32 __attribute__((thiscall)) fvm_vi(const FVM* s, tSigned32 f, tSigned32 v) { return s->idx[f*3+v]; }
static tSigned32 __attribute__((thiscall)) fvm_vx(const FVM* s, tSigned32 i) { return s->vx[i]; }
static tSigned32 __attribute__((thiscall)) fvm_vy(const FVM* s, tSigned32 i) { return s->vy[i]; }
static float __attribute__((thiscall)) fvm_vz(const FVM* s, tSigned32 i) { return s->vz[i]; }
static tSigned32 __attribute__((thiscall)) fvm_fa(const FVM*, tSigned32, tSigned32 a) { return (a==1)?0:-1; }
static void* fvmVt[] = {(void*)fvm_d,(void*)fvm_f,(void*)fvm_v,(void*)fvm_vi,(void*)fvm_vx,(void*)fvm_vy,(void*)fvm_vz,(void*)fvm_fa};

static tSigned32 tvx[] = {0,1000,1000,0};
static tSigned32 tvy[] = {0,0,1000,1000};
static float tvz[] = {0,0,0,0};
static tSigned32 tidx[] = {0,3,2, 0,2,1};

int main() {
    const char* path = "C:/Program Files (x86)/Steam/steamapps/common"
                       "/Titan Quest Anniversary Edition/pathengine.dll";
    HMODULE h = LoadLibraryA(path);
    if (!h) { printf("LoadLibrary FAIL err=%lu\n", GetLastError()); return 1; }
    typedef void* (__stdcall *GFn)(void*);
    auto gipe = (GFn)GetProcAddress(h, "_DllExport_GetIPathEngine@4");
    ErrorHandler eh = {g_errHandlerVtbl};
    void* pe = gipe(&eh);

    FVM fvm = {fvmVt, 2, 4, tidx, tvx, tvy, tvz};
    void* fp[] = {&fvm};
    typedef void* (__attribute__((thiscall)) *BMFn)(void*, void**, tUnsigned32, const char*const*);
    void* mesh = ((BMFn)(*(void***)pe)[10])(pe, fp, 1, nullptr);

    printf("DLL base: %p\n", (void*)h);
    printf("Mesh vtable (indices 0-70):\n");
    void** vtbl = *(void***)mesh;
    for (int i = 0; i <= 70; i++) {
        printf("  [%2d] = %p (RVA 0x%05lx)\n", i, vtbl[i], (unsigned long)((char*)vtbl[i] - (char*)h));
    }

    typedef void (__attribute__((thiscall)) *DFn)(void*);
    ((DFn)vtbl[0])(mesh);
    FreeLibrary(h);
    return 0;
}
