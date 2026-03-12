
import os

shim_path = os.path.join(os.path.dirname(__file__), 'pathengine_shim.cpp')
with open(shim_path, 'w') as f:
    f.write(r"""// pathengine_shim.cpp - Load pathengine.dll and generate nav mesh preprocess
// Build (32-bit): g++ -o pathengine_shim.exe pathengine_shim.cpp -static-libgcc -static-libstdc++
// Must be 32-bit to load TQ's 32-bit pathengine.dll

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <windows.h>

typedef long tSigned32;
typedef unsigned long tUnsigned32;

class iPathEngine;
class iMesh;
class iShape;

class iErrorHandler {
public:
    virtual ~iErrorHandler() {}
    virtual tSigned32 handle(const char* type, const char* desc, const char* const* attrs) {
        fprintf(stderr, "PE ERROR [%s]: %s\n", type ? type : "?", desc ? desc : "?");
        if (attrs) {
            for (int i = 0; attrs[i]; i += 2)
                fprintf(stderr, "  %s = %s\n", attrs[i], attrs[i+1] ? attrs[i+1] : "null");
        }
        return 0;
    }
};

class iFaceVertexMesh {
public:
    virtual ~iFaceVertexMesh() {}
    virtual tSigned32 faces() const = 0;
    virtual tSigned32 vertices() const = 0;
    virtual tSigned32 vertexIndex(tSigned32 face, tSigned32 vif) const = 0;
    virtual tSigned32 vertexX(tSigned32 vi) const = 0;
    virtual tSigned32 vertexY(tSigned32 vi) const = 0;
    virtual float vertexZ(tSigned32 vi) const = 0;
    virtual tSigned32 faceAttribute(tSigned32 face, tSigned32 attrIdx) const = 0;
};

class iOutputStream {
public:
    virtual ~iOutputStream() {}
    virtual void put(const char* data, tUnsigned32 size) = 0;
};

// Simple flat square mesh for testing
class TestSquareMesh : public iFaceVertexMesh {
    tSigned32 vx[4] = {0, 1000, 1000, 0};
    tSigned32 vy[4] = {0, 0, 1000, 1000};
    float vz[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    tSigned32 fi[6] = {0,1,2, 0,2,3};
public:
    tSigned32 faces() const override { return 2; }
    tSigned32 vertices() const override { return 4; }
    tSigned32 vertexIndex(tSigned32 face, tSigned32 vif) const override { return fi[face*3+vif]; }
    tSigned32 vertexX(tSigned32 vi) const override { return vx[vi]; }
    tSigned32 vertexY(tSigned32 vi) const override { return vy[vi]; }
    float vertexZ(tSigned32 vi) const override { return vz[vi]; }
    tSigned32 faceAttribute(tSigned32, tSigned32 attrIdx) const override {
        if (attrIdx == 1) return 0;
        return -1;
    }
};

class BufferOutputStream : public iOutputStream {
public:
    char* data; tUnsigned32 size; tUnsigned32 capacity;
    BufferOutputStream() : data(nullptr), size(0), capacity(0) {}
    ~BufferOutputStream() { free(data); }
    void put(const char* d, tUnsigned32 s) override {
        if (size + s > capacity) { capacity = (size + s) * 2; data = (char*)realloc(data, capacity); }
        memcpy(data + size, d, s);
        size += s;
    }
};

typedef iPathEngine* (__stdcall *GetIPathEngineFn)(iErrorHandler*);

template<typename Ret, typename... Args>
Ret callVt(void* obj, int idx, Args... args) {
    typedef Ret (__thiscall *Fn)(void*, Args...);
    return ((Fn)(*(void***)obj)[idx])(obj, args...);
}

int main(int argc, char** argv) {
    const char* dll_path = "C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\pathengine.dll";
    if (argc > 1) dll_path = argv[1];

    printf("=== PathEngine Shim ===\n");
    printf("sizeof(void*)=%zu\n", sizeof(void*));
    printf("Loading: %s\n", dll_path);

    HMODULE hDll = LoadLibraryA(dll_path);
    if (!hDll) { printf("LoadLibrary FAILED err=%lu\n", GetLastError()); return 1; }
    printf("DLL loaded at %p\n", hDll);

    auto getIPE = (GetIPathEngineFn)GetProcAddress(hDll, "_DllExport_GetIPathEngine@4");
    if (!getIPE) { printf("GetProcAddress FAILED\n"); return 1; }

    iErrorHandler errHandler;
    iPathEngine* pe = getIPE(&errHandler);
    if (!pe) { printf("GetIPathEngine returned null\n"); return 1; }
    printf("iPathEngine* = %p\n", pe);

    // Vtable[1]=getInterfaceMajorVersion, [2]=getInterfaceMinorVersion
    tSigned32 maj = callVt<tSigned32>(pe, 1);
    tSigned32 min_v = callVt<tSigned32>(pe, 2);
    printf("Interface version: %ld.%ld\n", maj, min_v);

    // Vtable[3]=getReleaseNumbers
    tSigned32 rMaj=0, rMin=0, rInt=0;
    typedef void (__thiscall *GetRelFn)(void*, tSigned32*, tSigned32*, tSigned32*);
    ((GetRelFn)((*(void***)pe)[3]))(pe, &rMaj, &rMin, &rInt);
    printf("Release: %ld.%ld.%ld\n", rMaj, rMin, rInt);

    // Build mesh from test square
    printf("\n--- buildMeshFromContent (test square) ---\n");
    TestSquareMesh testMesh;
    const iFaceVertexMesh* meshPtr = &testMesh;
    iMesh* mesh = callVt<iMesh*>(pe, 10, &meshPtr, (tUnsigned32)1, (const char*const*)nullptr);
    if (!mesh) { printf("buildMeshFromContent FAILED\n"); return 1; }
    printf("iMesh* = %p\n", mesh);

    // Create agent shape
    tSigned32 shapeCoords[] = {20,20, 20,-20, -20,-20, -20,20};
    iShape* shape = callVt<iShape*>(pe, 8, shapeCoords, (tUnsigned32)8);
    if (!shape) { printf("newShape FAILED\n"); return 1; }
    printf("iShape* = %p\n", shape);

    // Generate preprocess
    printf("generateUnobstructedSpaceFor...\n");
    callVt<void>(mesh, 43, shape, false, (const char*const*)nullptr);
    printf("generatePathfindPreprocessFor...\n");
    callVt<void>(mesh, 47, shape, (const char*const*)nullptr);
    printf("Done.\n");

    // Save preprocess
    BufferOutputStream ppStream;
    typedef void (__thiscall *SavePPFn)(void*, iShape*, iOutputStream*);
    ((SavePPFn)((*(void***)mesh)[54]))(mesh, shape, &ppStream);
    printf("Pathfind preprocess: %lu bytes\n", ppStream.size);

    // Save ground as TOK
    BufferOutputStream gndStream;
    typedef void (__thiscall *SaveGndFn)(void*, const char*, bool, iOutputStream*);
    ((SaveGndFn)((*(void***)mesh)[35]))(mesh, "tok", false, &gndStream);
    printf("Ground TOK: %lu bytes\n", gndStream.size);

    // Write preprocess to file if requested
    if (argc > 2) {
        FILE* fp = fopen(argv[2], "wb");
        if (fp) {
            fwrite(ppStream.data, 1, ppStream.size, fp);
            fclose(fp);
            printf("Wrote preprocess to %s\n", argv[2]);
        }
    }

    if (argc > 3) {
        FILE* fp = fopen(argv[3], "wb");
        if (fp) {
            fwrite(gndStream.data, 1, gndStream.size, fp);
            fclose(fp);
            printf("Wrote ground TOK to %s\n", argv[3]);
        }
    }

    callVt<void>(shape, 0);
    callVt<void>(mesh, 0);
    FreeLibrary(hDll);
    printf("\n=== Done ===\n");
    return 0;
}
""")
print(f"Written: {shim_path}")
