# Vertex element semantics, used to identify the meaning of vertex buffer
# contents
VES_POSITION = 1
VES_BLEND_WEIGHTS = 2
VES_BLEND_INDICES = 3
VES_NORMAL = 4
VES_DIFFUSE = 5
VES_SPECULAR = 6
VES_TEXTURE_COORDINATES = 7
VES_BINORMAL = 8
VES_TANGENT = 9

class MeshChunkID(object):
        Header = 0x1000
        Mesh = 0x3000
        SubMesh = 0x4000
        SubMeshOperation = 0x4010
        SubMeshBoneAssignment = 0x4100
        Geometry = 0x5000
        GeometryVertexDeclaration = 0x5100
        GeometryNormals = 0x5100
        GeometryVertexElement = 0x5110
        GeometryVertexBuffer = 0x5200
        GeometryColors = 0x5200
        GeometryVertexBufferData = 0x5210
        GeometryTexCoords = 0x5300
        MeshSkeletonLink = 0x6000
        MeshBoneAssignment = 0x7000
        MeshLOD = 0x8000
        MeshLODUsage = 0x8100
        MeshLODManual = 0x8110
        MeshLODGenerated = 0x8120
        MeshBounds = 0x9000
        SubMeshNameTable = 0xA000
        SubMeshNameTableElement = 0xA100
        EdgeLists = 0xB000
        EdgeListLOD = 0xB100
        EdgeListGroup = 0xB110

MeshCids = [MeshChunkID.Geometry, MeshChunkID.SubMesh,
            MeshChunkID.MeshSkeletonLink, MeshChunkID.MeshBoneAssignment,
            MeshChunkID.MeshLOD, MeshChunkID.MeshBounds,
            MeshChunkID.SubMeshNameTable, MeshChunkID.EdgeLists]

GeomCids = [MeshChunkID.GeometryVertexDeclaration,
            MeshChunkID.GeometryVertexBuffer]

SubMeshCids = [MeshChunkID.MeshBoneAssignment, MeshChunkID.SubMeshOperation]
