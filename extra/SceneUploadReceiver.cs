using System;
using System.IO;
using System.Collections.Generic;
using System.Text;
using OpenSim.Region.Framework.Interfaces;
using OpenSim.Region.Framework.Scenes;
using OpenSim.Region.Framework;
using OpenSim.Framework;
using System.Collections;
using OpenMetaverse;
using log4net;
using System.Reflection;
using Nwc.XmlRpc;
using System.Net;
using OgreSceneImporter;
using Ionic.Zip;

using ModularRex.RexFramework;
using ModularRex.RexNetwork;


namespace OgreSceneImporter
{
 //   delegate void AppearanceAddedDelegate(UUID agentID);

    public class SceneUploadReceiver : ISharedRegionModule
    {
        private static readonly ILog m_log =
            LogManager.GetLogger(MethodBase.GetCurrentMethod().DeclaringType);

        private List<Scene> m_scenes = new List<Scene>();
        private Scene m_scene;
        private bool m_initialised = false;
        private Dictionary<UUID, string> m_avatarUrls = new Dictionary<UUID, string>();
       // private event AppearanceAddedDelegate OnNewAvatarUrl;


        #region IRegionModuleBase Members

        public string Name
        {
            get { return "RexSceneUploadReceiver"; }
        }

        public Type ReplaceableInterface
        {
            get { return null; }
        }

        public bool IsSharedModule
	{
	           get { return true; }

	}


	public void Initialise(Nini.Config.IConfigSource source)
	{
        }

        public void InitialiseX(Scene scene, Nini.Config.IConfigSource source)
        {
	    m_scene = scene;
            m_log.Error("[SCENEIMPORT]: Add Initialise ");
	    m_log.Error(scene.Modules.ToString());
		       foreach (System.Collections.Generic.KeyValuePair<string,OpenSim.Region.Framework.Interfaces.IRegionModuleBase> entry in scene.RegionModules)
	       {
	                m_log.ErrorFormat("region modules[{0}]={1}", entry.Key, entry.Value);
	        }
	       foreach (System.Collections.Generic.KeyValuePair<string,OpenSim.Region.Framework.Interfaces.IRegionModule> entry in scene.Modules)
	       {
	                m_log.ErrorFormat("modules[{0}]={1}", entry.Key, entry.Value);
	        }

    //m_log.Error(scene.RegionModules["rex uploader module"].ToString());
           // this.OnNewAvatarUrl += new AppearanceAddedDelegate(AvatarUrlReciver_OnNewAvatarUrl);
        }

        public void Close()
        {
            //this.OnNewAvatarUrl -= new AppearanceAddedDelegate(AvatarUrlReciver_OnNewAvatarUrl);
        }

        public void AddRegion(OpenSim.Region.Framework.Scenes.Scene scene)
        {
            m_log.Error("[SCENEIMPORT]: Add Region: ");
            m_scenes.Add(scene);
	    m_scene = scene;

 //           scene.EventManager.OnClientConnect += new EventManager.OnClientConnectCoreDelegate(HandleOnClientConnect);
        }

        public void RemoveRegion(OpenSim.Region.Framework.Scenes.Scene scene)
        {
            m_scenes.Remove(scene);

 //           scene.EventManager.OnClientConnect -= new EventManager.OnClientConnectCoreDelegate(HandleOnClientConnect);
        }

        public void RegionLoaded(OpenSim.Region.Framework.Scenes.Scene scene)
        {
		if (!m_initialised) {
            	    MainServer.Instance.AddXmlRPCHandler("ogrescene_upload", XmlRpcHandler);
            	    MainServer.Instance.AddXmlRPCHandler("ogrescene_list", ListXmlRpcHandler);
            	    MainServer.Instance.AddXmlRPCHandler("ogrescene_clear", ClearXmlRpcHandler);
		    m_initialised = true;
		}
        }

        #endregion

        private void TriggerOnNewAvatarUrl(UUID agentID)
        {
           /* try
            {
                if (OnNewAvatarUrl != null)
                {
                    OnNewAvatarUrl(agentID);
                }
            }
            catch (Exception e)
            {
                m_log.Error("[REXAVATARURL]: Error triggering OnNewAvatarUrl event: " + e.Message);
            }*/
        }

	private OpenSim.Region.Framework.Scenes.Scene SelectRegion(UUID regionID)
	{
		foreach (OpenSim.Region.Framework.Scenes.Scene scene in m_scenes) {
			if (scene.RegionInfo.RegionID == regionID) {
				return scene;
			}

		}
		return null;
	}

        public XmlRpcResponse ClearXmlRpcHandler(XmlRpcRequest request, IPEndPoint client)
	{
  	    // AuthClient.VerifySession(GetUserServerURL(userID), userID, sessionID);
            XmlRpcResponse response = new XmlRpcResponse();
            Hashtable requestData = (Hashtable)request.Params[0];
            Hashtable resp = new Hashtable();
            if (requestData.ContainsKey("RegionID"))
	    {
		    UUID regionID = UUID.Parse((string)requestData["RegionID"]);
		    m_scene = SelectRegion(regionID);
		    m_scene.DeleteAllSceneObjects();
	    }
	    else
	    {
		    resp["success"] = false;
		    resp["error"] = "no RegionID provided";
		    response.Value = resp;
                    return response;
	    }
	    // return ok;
	    m_log.Info("Region Cleared: " + requestData["RegionID"].ToString());
            resp["success"] = true;
	    response.Value = resp;
	    return response;
	}
        public XmlRpcResponse ListXmlRpcHandler(XmlRpcRequest request, IPEndPoint client)
	{
  	    // AuthClient.VerifySession(GetUserServerURL(userID), userID, sessionID);
            XmlRpcResponse response = new XmlRpcResponse();
            Hashtable requestData = (Hashtable)request.Params[0];
            Hashtable resp = new Hashtable();
	    Hashtable result = new Hashtable();
            if (requestData.ContainsKey("RegionID"))
	    {
		    UUID regionID = UUID.Parse((string)requestData["RegionID"]);
		    m_scene = SelectRegion(regionID);

                    IModrexObjectsProvider rexObjects = m_scene.RequestModuleInterface<IModrexObjectsProvider>();

		    m_scene.ForEachSOG(delegate(SceneObjectGroup e)
		    {
		    	Hashtable sogdata = new Hashtable();
			sogdata["name"] = e.Name;
			sogdata["groupid"] = e.GroupID.ToString();
			sogdata["primcount"] = e.PrimCount.ToString();
			sogdata["owner"] = e.OwnerID.ToString();
			sogdata["part"] = e.GetFromItemID().ToString();

                        RexObjectProperties robject = rexObjects.GetObject(e.RootPart.UUID);
                        sogdata["asset"] = robject.RexMeshUUID.ToString();
                        sogdata["distance"] = robject.RexDrawDistance.ToString();
			if (robject.RexMaterials.Count > 0) {
				Hashtable materials = new Hashtable();
				foreach (uint matindex in robject.RexMaterials.Keys) {
					materials[robject.RexMaterials[matindex].AssetID.ToString()] = robject.RexMaterials[matindex].AssetURI;
					AssetBase asset = m_scene.AssetService.Get(robject.RexMaterials[matindex].AssetID.ToString());
					materials[robject.RexMaterials[matindex].AssetID.ToString()+"_d"] = asset.Description;
					materials[robject.RexMaterials[matindex].AssetID.ToString()+"_data"] = (byte[])asset.Data;
				}
				sogdata["materials"] = materials;
			}
 //                       robject.RexCastShadows = ent.CastShadows;
   //                     robject.RexDrawType = 1;

		    	result[e.UUID.ToString()] = sogdata;
		    });
            	    resp["res"] = result;
		    // m_scene.DeleteAllSceneObjects();
	    }
	    else
	    {
		    resp["success"] = false;
		    resp["error"] = "no RegionID provided";
		    response.Value = resp;
                    return response;
	    }
	    // return ok;
	    m_log.Info("Region Cleared: " + requestData["RegionID"].ToString());
            resp["success"] = true;
	    response.Value = resp;
	    return response;
	}

        public XmlRpcResponse XmlRpcHandler(XmlRpcRequest request, IPEndPoint client)
        {
  	    // AuthClient.VerifySession(GetUserServerURL(userID), userID, sessionID);
	    m_log.Info("[SCENEUPLOADER] Loading Scenex");
            XmlRpcResponse response = new XmlRpcResponse();
            Hashtable requestData = (Hashtable)request.Params[0];
            Hashtable resp = new Hashtable();
            resp["success"] = false;
            resp["error"] = String.Empty;
	    m_log.Info("[SCENEUPLOADER] Parsing Request");

            if (requestData.ContainsKey("AgentID") &&
                requestData.ContainsKey("AvatarURL") && 
		requestData.ContainsKey("RegionID") && 
		requestData.ContainsKey("PackName"))
            {
                UUID agentID;
		UUID regionID = UUID.Parse((string)requestData["RegionID"]);
		m_scene = SelectRegion(regionID);
                string avatarUrl;
		string packName = (string)requestData["PackName"];
	        m_log.Info("[SCENEUPLOADER] Write zip file to disk ");
		FileStream fout = new FileStream("/tmp/test.zip", FileMode.Create);
		byte[] data = (byte[])requestData["AvatarURL"];
		fout.Write(data, 0, data.Length);
		fout.Close();

		Ionic.Zip.ZipFile f = null;
                try
		{
		     f = Ionic.Zip.ZipFile.Read("/tmp/test.zip");
		     f.ExtractAll("/tmp/foo");
		     f.Dispose();
                }
                catch (Exception)
                {
                     if (f != null)
                            f.Dispose();
                      throw;
                }


		OgreSceneImportModule osi = (OgreSceneImportModule)m_scene.Modules["OgreSceneImportModule"];
		osi.ImportUploadedOgreScene("/tmp/foo/" + packName, m_scene);

	        m_log.Info("[SCENEUPLOADER] Cleaning up");
		Directory.Delete("/tmp/foo", true);
		File.Delete("/tmp/test.zip");

                resp["success"] = true;
            }

            response.Value = resp;
	    m_log.Info("[SCENEUPLOADER] Scene Loaded" + requestData["PackName"].ToString());
            return response;
        }
        #region ISharedRegionModule Members

        public void PostInitialise()
        {
           try
            {
                m_log.Error("[SCENEIMPORT]: Initialised ");
            }
            catch (Exception e)
            {
                m_log.Error("[SCENEIMPORT]: Error triggering OnNewAvatarUrl event: " + e.Message);
            }

        }

        #endregion

        void HandleOnClientConnect(OpenSim.Framework.Client.IClientCore client)
        {
            if (m_avatarUrls.ContainsKey(client.AgentId))
            {
                IClientRexAppearance avatar;
                if (client.TryGet<IClientRexAppearance>(out avatar))
                {
                    avatar.RexAvatarURL = m_avatarUrls[client.AgentId];
                    m_log.InfoFormat("[REXSCENEUPLOAD]: Upload scene {0} to user {1}", avatar.RexAvatarURL, client.AgentId);
                }
            }
        }

        void AvatarUrlReciver_OnNewAvatarUrl(UUID agentID)
        {
            foreach (Scene scene in m_scenes)
            {
                scene.ForEachClient(delegate(IClientAPI client)
                {
                    if (client.AgentId == agentID)
                    {
                        if (client is IClientRexAppearance)
                        {
                            ((IClientRexAppearance)client).RexAvatarURL = m_avatarUrls[agentID];
                            m_log.InfoFormat("[REXAVATARURL]: Set avatar url {0} to user {1}", m_avatarUrls[agentID], agentID);
                        }
                    }
                });
            }
        }
    }
}
