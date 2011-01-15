import sys
import struct
import oserializer
import otypes
import StringIO
from otypes import MeshChunkID, MeshCids, GeomCids, SubMeshCids

def ReadGeometryVertexElement(serializer, reader):
    source = serializer.ReadShort(reader)
    VertexElementType = serializer.ReadShort(reader)
    semantic = serializer.ReadShort(reader)
    offset = serializer.ReadShort(reader)
    index = serializer.ReadShort(reader)
    return [source, offset, VertexElementType, semantic, index]

def ReadGeometryVertexBuffer(serializer, reader, vertexCount):
    bindIdx = serializer.ReadShort(reader)
    vertexSize = serializer.ReadShort(reader)
    cid = serializer.ReadChunk(reader)
    if cid != MeshChunkID.GeometryVertexBufferData:
        raise Exception("Missing vertex buffer data")
    return serializer.ReadBytes(reader, vertexSize*vertexCount)

def ReadGeometryVertexDeclaration(serializer, reader):
    vertex = []
    if not serializer.IsEOF(reader):
        cid = serializer.ReadChunk(reader)
        while cid in [MeshChunkID.GeometryVertexElement] and not serializer.IsEOF(reader):
            if cid == MeshChunkID.GeometryVertexElement:
                vertex.append(ReadGeometryVertexElement(serializer, reader))
            if not serializer.IsEOF(reader):
                cid = serializer.ReadChunk(reader)
        if not serializer.IsEOF(reader):
            serializer.Seek(reader, -serializer.ChunkOverheadSize)
    return vertex

def ReadGeometry(serializer, reader):
    vertexStart = 0
    vertexCount = serializer.ReadInt(reader)
    vertex = None
    vbuffer = None
    if not serializer.IsEOF(reader):
        cid = serializer.ReadChunk(reader)
        while cid in GeomCids and not serializer.IsEOF(reader):
            if cid == MeshChunkID.GeometryVertexDeclaration:
                vertex = ReadGeometryVertexDeclaration(serializer, reader)
            elif cid == MeshChunkID.GeometryVertexBuffer:
                vbuffer = ReadGeometryVertexBuffer(serializer, reader, vertexCount)
            if not serializer.IsEOF(reader):
                cid = serializer.ReadChunk(reader)
        if not serializer.IsEOF(reader):
            serializer.Seek(reader, -serializer.ChunkOverheadSize)
    return vertex, vbuffer

def ReadSubMesh(serializer, reader):
    cid = None
    materialName = serializer.ReadString(reader)
    useSharedVertices = serializer.ReadBool(reader)
    indexCount = serializer.ReadInt(reader)
    idx32bit = serializer.ReadBool(reader)
    vertex = None
    vbuffer = None
    if idx32bit:
        indices = int(serializer.ReadInts(reader, indexCount))
    else:
        indices = serializer.ReadShorts(reader, indexCount)
    if not useSharedVertices:
        cid = serializer.ReadChunk(reader)
        if cid != MeshChunkID.Geometry:
            raise Exception("Missing geometry data")
        vertex, vbuffer = ReadGeometry(serializer, reader)
    else:
        print "no shared!"
    cid = serializer.ReadChunk(reader)
    while not serializer.IsEOF(reader) and cid in SubMeshCids:
        if cid == MeshChunkID.SubMeshOperation:
            sys.stderr.write("o")
            sys.stderr.flush()
            serializer.ReadShort(reader)
        elif cid == MeshChunkID.SubMeshBoneAssignment:
            serializer.ReadInt(reader)
            serializer.ReadUShort(reader)
            serializer.ReadFloat(reader)
        if not serializer.IsEOF(reader):
            cid = serializer.ReadChunk(reader)
    if not serializer.IsEOF(reader):
        serializer.Seek(reader, -serializer.ChunkOverheadSize)
    return vertex, vbuffer, indices, materialName

def ReadMesh(serializer, reader):
    SkelAnimed = serializer.ReadBool(reader)
    cid = serializer.ReadChunk(reader)
    submeshes = []
    while cid in MeshCids and not serializer.IsEOF(reader):
        if cid == MeshChunkID.SubMesh:
            sys.stderr.write("s")
            submeshes.append(ReadSubMesh(serializer, reader))
        else:
            sys.stderr.write("i")
            serializer.IgnoreCurrentChunk(reader)
        cid = serializer.ReadChunk(reader)
    if not serializer.IsEOF(reader):
        serializer.Seek(reader, -serializer.ChunkOverheadSize)
    return submeshes
        
def parse(data):
    reader = StringIO.StringIO(data)
    serializer = oserializer.Serializer()
    meshes = []
    if serializer.ReadShort(reader) == MeshChunkID.Header:
        fileVersion = serializer.ReadString(reader)
        while not serializer.IsEOF(reader):
            cid = serializer.ReadChunk(reader)
            if cid == MeshChunkID.Mesh:
                meshes.append(ReadMesh(serializer, reader))
            else:
                #print "ignoring",cid
                serializer.IgnoreCurrentChunk(reader)
                #else:
                    #print "incorrect cid", cid
    else:
        #raise Exception("no header found")
        print "no header found"
        f = open("/tmp/noheader.txt","a")
        f.write(data+"\n-------------------\n")
        f.close()
    if meshes:
        return meshes[0]


