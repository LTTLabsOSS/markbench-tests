//-----------------------------------------------------------------------
//------------------- Copyright (c) samisalreadytaken -------------------
//                       github.com/samisalreadytaken
//-----------------------------------------------------------------------
local VERSION = "1.4.7";

IncludeScript("vs_library");

if ( !("_BM_"in getroottable()) )
	::_BM_ <- { version = VERSION };;

local _ = function(){

SendToConsole("alias benchmark\"script _BM_.Start()\"");
SendToConsole("alias bm_start\"script _BM_.Start(1)\"");
SendToConsole("alias bm_stop\"script _BM_.Stop()\"");
SendToConsole("alias bm_timer\"script _BM_.ToggleCounter()\"");
SendToConsole("alias bm_setup\"script _BM_.PrintSetupCmd()\"");
SendToConsole("alias bm_list\"script _BM_.ListSetupData()\"");
SendToConsole("alias bm_clear\"script _BM_.ClearSetupData()\"");
SendToConsole("alias bm_remove\"script _BM_.RemoveSetupData()\"");

SendToConsole("alias bm_mdl\"script _BM_.PrintMDL()\"");
SendToConsole("alias bm_mdl1\"script _BM_.PrintMDL(1)\"");
SendToConsole("alias bm_flash\"script _BM_.PrintFlash()\"");
SendToConsole("alias bm_flash1\"script _BM_.PrintFlash(1)\"");
SendToConsole("alias bm_he\"script _BM_.PrintHE()\"");
SendToConsole("alias bm_he1\"script _BM_.PrintHE(1)\"");
SendToConsole("alias bm_molo\"script _BM_.PrintMolo()\"");
SendToConsole("alias bm_molo1\"script _BM_.PrintMolo(1)\"");
SendToConsole("alias bm_smoke\"script _BM_.PrintSmoke()\"");
SendToConsole("alias bm_smoke1\"script _BM_.PrintSmoke(1)\"");
SendToConsole("alias bm_expl\"script _BM_.PrintExpl()\"");
SendToConsole("alias bm_expl1\"script _BM_.PrintExpl(1)\"");

// deprecated
_VER_ <- version;
SendToConsole("alias bm_rec\"script _BM_.Record()\"");

//--------------------------------------------------------------

SendToConsole("clear;script _BM_.PostSpawn()");

if ( !("m_bPlayback" in this) )
{
	g_FrameTime <- 0.015625;
	SND_BUTTON <- "UIPanorama.XP.Ticker";
	Fmt <- format;
	Msg <- print;
	EntFireByHandle <- EntFireByHandle;
	ClientCommand <- SendToConsole;

	m_FileBuffer <- { V = Vector, Q = dummy }
	m_fnSetup <- null;
	m_DataBuffer <- {};
	m_PathData <- [];
	m_nPlaybackIdx <- 0;
	m_nPlaybackTarget <- 0;
	m_bPlaybackPending <- false;
	m_bPlayback <- false;
	m_nPlaybackType <- 0;
	m_bLooping <- false;
	m_nMaxFPS <- 0;
	m_flTimeStart <- 0.0;
	m_iDev <- 0;
	m_iRecLast <- 0;
	m_nCounterCount <- 0;
	m_flTargetLength <- 0.0;
	m_list_models <- null;
	m_list_nades <- null;
};

if ( !("m_hThink" in this) )
{
	g_szMapName <- split( GetMapName(), "/" ).top();
	g_flTickrate <- 1.0 / FrameTime();

	m_hStrip <- VS.CreateEntity( "game_player_equip",{ spawnflags = 1<<1 }, 1 ).weakref();
	m_hHudHint <- VS.CreateEntity( "env_hudhint", null, 1 ).weakref();
	m_hCam <- VS.CreateEntity( "point_viewcontrol",{ spawnflags = 1<<3 } ).weakref();
	m_hThink <- VS.Timer( 1, g_FrameTime, null, null, 1, 1 ).weakref();
	m_hCounter <- null;
};

m_szLastError <- null;
player <- VS.GetPlayerByIndex(1);

//--------------------------------------------------------------

MDL <-
{
	FBIa  = "models/player/custom_player/legacy/ctm_fbi_varianta.mdl",
	FBIb  = "models/player/custom_player/legacy/ctm_fbi_variantb.mdl",
	FBIc  = "models/player/custom_player/legacy/ctm_fbi_variantc.mdl",
	FBId  = "models/player/custom_player/legacy/ctm_fbi_variantd.mdl",
	FBIe  = "models/player/custom_player/legacy/ctm_fbi_variante.mdl",
	FBIf  = "models/player/custom_player/legacy/ctm_fbi_variantf.mdl",
	FBIg  = "models/player/custom_player/legacy/ctm_fbi_variantg.mdl",
	FBIh  = "models/player/custom_player/legacy/ctm_fbi_varianth.mdl",

	GIGNa = "models/player/custom_player/legacy/ctm_gign_varianta.mdl",
	GIGNb = "models/player/custom_player/legacy/ctm_gign_variantb.mdl",
	GIGNc = "models/player/custom_player/legacy/ctm_gign_variantc.mdl",
	GIGNd = "models/player/custom_player/legacy/ctm_gign_variantd.mdl",

	GSG9a = "models/player/custom_player/legacy/ctm_gsg9_varianta.mdl",
	GSG9b = "models/player/custom_player/legacy/ctm_gsg9_variantb.mdl",
	GSG9c = "models/player/custom_player/legacy/ctm_gsg9_variantc.mdl",
	GSG9d = "models/player/custom_player/legacy/ctm_gsg9_variantd.mdl",

	IDFb  = "models/player/custom_player/legacy/ctm_idf_variantb.mdl",
	IDFc  = "models/player/custom_player/legacy/ctm_idf_variantc.mdl",
	IDFd  = "models/player/custom_player/legacy/ctm_idf_variantd.mdl",
	IDFe  = "models/player/custom_player/legacy/ctm_idf_variante.mdl",
	IDFf  = "models/player/custom_player/legacy/ctm_idf_variantf.mdl",

	SASa  = "models/player/custom_player/legacy/ctm_sas_varianta.mdl",
	SASb  = "models/player/custom_player/legacy/ctm_sas_variantb.mdl",
	SASc  = "models/player/custom_player/legacy/ctm_sas_variantc.mdl",
	SASd  = "models/player/custom_player/legacy/ctm_sas_variantd.mdl",
	SASe  = "models/player/custom_player/legacy/ctm_sas_variante.mdl",
	SASf  = "models/player/custom_player/legacy/ctm_sas_variantf.mdl",

	ST6a  = "models/player/custom_player/legacy/ctm_st6_varianta.mdl",
	ST6b  = "models/player/custom_player/legacy/ctm_st6_variantb.mdl",
	ST6c  = "models/player/custom_player/legacy/ctm_st6_variantc.mdl",
	ST6d  = "models/player/custom_player/legacy/ctm_st6_variantd.mdl",
	ST6e  = "models/player/custom_player/legacy/ctm_st6_variante.mdl",
	ST6g  = "models/player/custom_player/legacy/ctm_st6_variantg.mdl",
	ST6i  = "models/player/custom_player/legacy/ctm_st6_varianti.mdl",
	ST6k  = "models/player/custom_player/legacy/ctm_st6_variantk.mdl",
	ST6m  = "models/player/custom_player/legacy/ctm_st6_variantm.mdl",

	SWATa = "models/player/custom_player/legacy/ctm_swat_varianta.mdl",
	SWATb = "models/player/custom_player/legacy/ctm_swat_variantb.mdl",
	SWATc = "models/player/custom_player/legacy/ctm_swat_variantc.mdl",
	SWATd = "models/player/custom_player/legacy/ctm_swat_variantd.mdl",

	ANARa = "models/player/custom_player/legacy/tm_anarchist_varianta.mdl",
	ANARb = "models/player/custom_player/legacy/tm_anarchist_variantb.mdl",
	ANARc = "models/player/custom_player/legacy/tm_anarchist_variantc.mdl",
	ANARd = "models/player/custom_player/legacy/tm_anarchist_variantd.mdl",

	BALKa = "models/player/custom_player/legacy/tm_balkan_varianta.mdl",
	BALKb = "models/player/custom_player/legacy/tm_balkan_variantb.mdl",
	BALKc = "models/player/custom_player/legacy/tm_balkan_variantc.mdl",
	BALKd = "models/player/custom_player/legacy/tm_balkan_variantd.mdl",
	BALKe = "models/player/custom_player/legacy/tm_balkan_variante.mdl",
	BALKf = "models/player/custom_player/legacy/tm_balkan_variantf.mdl",
	BALKg = "models/player/custom_player/legacy/tm_balkan_variantg.mdl",
	BALKh = "models/player/custom_player/legacy/tm_balkan_varianth.mdl",
	BALKi = "models/player/custom_player/legacy/tm_balkan_varianti.mdl",
	BALKj = "models/player/custom_player/legacy/tm_balkan_variantj.mdl",

	LEETa = "models/player/custom_player/legacy/tm_leet_varianta.mdl",
	LEETb = "models/player/custom_player/legacy/tm_leet_variantb.mdl",
	LEETc = "models/player/custom_player/legacy/tm_leet_variantc.mdl",
	LEETd = "models/player/custom_player/legacy/tm_leet_variantd.mdl",
	LEETe = "models/player/custom_player/legacy/tm_leet_variante.mdl",
	LEETf = "models/player/custom_player/legacy/tm_leet_variantf.mdl",
	LEETg = "models/player/custom_player/legacy/tm_leet_variantg.mdl",
	LEETh = "models/player/custom_player/legacy/tm_leet_varianth.mdl",
	LEETi = "models/player/custom_player/legacy/tm_leet_varianti.mdl",

	PHXa  = "models/player/custom_player/legacy/tm_phoenix_varianta.mdl",
	PHXb  = "models/player/custom_player/legacy/tm_phoenix_variantb.mdl",
	PHXc  = "models/player/custom_player/legacy/tm_phoenix_variantc.mdl",
	PHXd  = "models/player/custom_player/legacy/tm_phoenix_variantd.mdl",
	PHXf  = "models/player/custom_player/legacy/tm_phoenix_variantf.mdl",
	PHXg  = "models/player/custom_player/legacy/tm_phoenix_variantg.mdl",
	PHXh  = "models/player/custom_player/legacy/tm_phoenix_varianth.mdl",

	PRTa  = "models/player/custom_player/legacy/tm_pirate_varianta.mdl",
	PRTb  = "models/player/custom_player/legacy/tm_pirate_variantb.mdl",
	PRTc  = "models/player/custom_player/legacy/tm_pirate_variantc.mdl",
	PRTd  = "models/player/custom_player/legacy/tm_pirate_variantd.mdl",

	PROa  = "models/player/custom_player/legacy/tm_professional_var1.mdl",
	PROb  = "models/player/custom_player/legacy/tm_professional_var2.mdl",
	PROc  = "models/player/custom_player/legacy/tm_professional_var3.mdl",
	PROd  = "models/player/custom_player/legacy/tm_professional_var4.mdl",

	SEPa  = "models/player/custom_player/legacy/tm_separatist_varianta.mdl",
	SEPb  = "models/player/custom_player/legacy/tm_separatist_variantb.mdl",
	SEPc  = "models/player/custom_player/legacy/tm_separatist_variantc.mdl",
	SEPd  = "models/player/custom_player/legacy/tm_separatist_variantd.mdl",

	H_CT  = "models/player/custom_player/legacy/ctm_heavy.mdl",
	H_T   = "models/player/custom_player/legacy/tm_phoenix_heavy.mdl"
}

POSE <-
{
	DEFAULT = 0,
	ROM     = 1,
	A       = 2,
	PISTOL  = 3,
	RIFLE   = 4
}

//--------------------------------------------------------------

class point_t
{
	origin = null;
	angles = null;
}

function LoadData()
{
	m_DataBuffer.clear();
	m_fnSetup = null;

	try( DoIncludeScript( "benchmark_res", m_FileBuffer ) )
	catch(e)
	{
		// not mandatory
	}

	// Load bm_mapname.nut by default
	try( DoIncludeScript( "bm_"+g_szMapName+".nut", m_DataBuffer ) )
	catch(x)
	{
		// Check if data named bm_mapname is manually loaded in the resource file

		local dataName = "bm_"+g_szMapName;
		if ( !(dataName in m_FileBuffer) )
		{
			// alternative prefix
			dataName = "l_" + g_szMapName;

			if ( !(dataName in m_FileBuffer) )
			{
				m_szLastError = Fmt( "[!] Map data not found for '%s'\n", g_szMapName );
				return;
			};
		};

		m_DataBuffer[0] <- delete m_FileBuffer[dataName];
	}

	if ( !m_DataBuffer.len() )
	{
		m_szLastError = "[!] Empty data file\n";
		return;
	};

	local pInput;
	local nVersion = -1;

	foreach( v in m_DataBuffer )
	{
		if ( "version" in v )
		{
			pInput = v;
			nVersion = v.version;
			break;
		};
	}

	if ( !pInput )
	{
		m_szLastError = "[!] Empty data file\n";
		return;
	};

	// KF_SAVE_V2
	if ( nVersion != 2 )
	{
		m_szLastError = Fmt( "[!] Unrecognised data version %d (expected %d)\n", nVersion, 2 );
		m_szLastError += "[i] Convert your data using ( github.com/samisalreadytaken/keyframes )\n";
		return;
	};

	// Parse
	m_PathData.clear();
	m_PathData.resize( pInput.framecount );

	local pData = pInput.frames;
	local c = pData.len();
	local frame = 0;

	for ( local i = 0; i < c; )
	{
		local p = point_t();
		m_PathData[ frame++ ] = p;

		local n = pData[i++];

		p.origin = Vector( pData[i],	pData[i+1],	pData[i+2] );
		p.angles = Vector( pData[i+3],	pData[i+4],	pData[i+5] );

		i += (n & 0x01) ? 8 : 6;
	}

	// Assert
	local c = m_PathData.len();
	for ( local i = 0; i < c; i++ )
	{
		if ( !m_PathData[i] )
		{
			m_PathData.resize( i-1 );
			break;
		};
	}

	m_nPlaybackTarget = m_PathData.len();
	m_flTargetLength = m_nPlaybackTarget * g_FrameTime;

	if ( !m_nPlaybackTarget )
	{
		m_szLastError = "[!] Empty path data.\n";
	};

	local fn = "Setup_" + g_szMapName;
	if ( "Setup" in m_DataBuffer )
	{
		m_fnSetup = m_DataBuffer.Setup;
	}
	else if ( fn in m_DataBuffer )
	{
		m_fnSetup = m_DataBuffer[fn];
	};;

	// Let the _res file overwrite setup functions
	if ( fn in m_FileBuffer )
	{
		m_fnSetup = m_FileBuffer[fn];
	};

	m_DataBuffer.clear();
	m_FileBuffer.clear();
	m_FileBuffer.V <- Vector;
	m_FileBuffer.Q <- dummy;
}

//--------------------------------------------------------------

function PlaySound(s)
{
	return player.EmitSound(s);
}

function Hint(s)
{
	m_hHudHint.__KeyValueFromString( "message", s );
	return EntFireByHandle( m_hHudHint, "ShowHudHint", "", 0.0, player );
}

function SetLooping(i)
{
	m_bLooping = !!i;
}

function SetMaxFPS(i)
{
	if ( i < 0 && i != -1 )
		i = 0;

	m_nMaxFPS = i;
}

function ToggleCounter( i = null )
{
	if ( !m_hCounter )
	{
		if ( i != null && !i )
			return;

		m_hCounter = VS.Timer( 1, 1, function()
		{
			Hint( "" + (++m_nCounterCount) );
			PlaySound("UIPanorama.container_countdown");
		}, this, 0, 1 ).weakref();
	};

	// toggle
	if ( i == null )
		i = !m_hCounter.GetTeam();

	m_hCounter.SetTeam( i.tointeger() );
	m_nCounterCount = 0;

	EntFireByHandle( m_hCounter, i ? "Enable" : "Disable" );
}

VS.OnTimer( m_hThink, function()
{
	local pt = m_PathData[m_nPlaybackIdx];
	m_hCam.SetAbsOrigin( pt.origin );

	local a = pt.angles;
	m_hCam.SetAngles( a.x, a.y, a.z );
	player.SetAngles( a.x, a.y, 0.0 );

	if ( m_nPlaybackTarget <= ++m_nPlaybackIdx )
	{
		if ( !m_bLooping )
			return Stop(1);

		if ( !m_nPlaybackType && m_fnSetup )
			m_fnSetup.call(this);

		m_nPlaybackIdx = 0;
	};

}, this );

function Record()
{
	Msg("Recording is not available in the benchmark script.\n");
	Msg("Use the keyframes script to create smooth camera paths:\n");
	Msg("                github.com/samisalreadytaken/keyframes\n");
}

function ErrorCheck()
{
	if ( m_szLastError )
	{
		Msg( m_szLastError );
		return false;
	};
	return true;
}

function Start( bPathOnly = 0 )
{
	if ( m_bPlaybackPending )
		return Msg("Benchmark has not started yet.\n");

	if ( m_bPlayback )
		return Msg("Benchmark is already running!\nTo stop it: bm_stop\n");

	if ( !ErrorCheck() )
		return;

	m_nMaxFPS = 0;
	m_bLooping = false;
	m_nPlaybackType = bPathOnly;

	EntFireByHandle( m_hThink, "Disable" );
	m_nPlaybackIdx = 0;

	EntFireByHandle( m_hStrip, "Use", "", 0, player );
	player.SetHealth(1337);

	if ( !bPathOnly && m_fnSetup )
	{
		m_fnSetup.call(this);
	};

	m_bPlaybackPending = true;
	m_iDev = GetDeveloperLevel();

	local snd = [this, "Alert.WarmupTimeoutBeep"];

	VS.EventQueue.AddEvent( Hint, 0.5, [this, "Starting in 3..."] );
	VS.EventQueue.AddEvent( PlaySound, 0.5, snd );

	VS.EventQueue.AddEvent( Hint, 1.5, [this, "Starting in 2..."] );
	VS.EventQueue.AddEvent( PlaySound, 1.5, snd );

	VS.EventQueue.AddEvent( Hint, 2.5, [this, "Starting in 1..."] );
	VS.EventQueue.AddEvent( PlaySound, 2.5, snd );

	EntFireByHandle( m_hHudHint, "HideHudHint", "", 3.5, player );

	VS.EventQueue.AddEvent( PlaySound, 0.5, [this, "Weapon_AWP.BoltForward"] );
	PlaySound("Weapon_AWP.BoltBack");

	ClientCommand(Fmt( "r_cleardecals%s;clear;echo;echo;echo;echo\"   Starting in 3 seconds...\";echo;developer 0;hideconsole;fadeout",
		(m_nMaxFPS != -1 ? ";fps_max "+m_nMaxFPS : "") ));

	VS.EventQueue.AddEvent( StartInternal, 3.5, this );
}

function StartInternal()
{
	m_bPlaybackPending = false;
	m_bPlayback = true;
	m_flTimeStart = Time();
	EntFireByHandle( m_hCam, "Enable", "", 0, player );
	EntFireByHandle( m_hThink, "Enable" );
	ClientCommand("fadein;bench_start;bench_end;host_framerate 0;host_timescale 1;clear;echo;echo;echo;echo\"   Benchmark has started\";echo;echo");
}

function Stop( bAuto = 0 )
{
	if ( m_bPlaybackPending )
	{
		m_bPlaybackPending = false;
		ClientCommand("fadein");
		VS.EventQueue.CancelEventsByInput( StartInternal );
		VS.EventQueue.CancelEventsByInput( Hint );
		VS.EventQueue.CancelEventsByInput( PlaySound );
		EntFireByHandle( m_hHudHint, "HideHudHint", "", 0.0, player );
	}
	else if ( !m_bPlayback )
		return Msg("Benchmark is not running.\n");;

	m_bPlayback = false;

	VS.EventQueue.CancelEventsByInput( Dispatch );
	ClientCommand( "ent_cancelpendingentfires" );

	EntFireByHandle( m_hCam, "Disable", "", 0, player );
	EntFireByHandle( m_hThink, "Disable" );
	ToggleCounter(0);

	local szOutTime;
	local flDiff = Time() - m_flTimeStart;

	if ( flDiff == m_flTargetLength || m_bLooping )
	{
		szOutTime = flDiff + " seconds";
	}
	else
	{
		szOutTime = Fmt( "%g seconds (expected: %g)", flDiff, m_flTargetLength );
	};

	ClientCommand("host_framerate 0;host_timescale 1");
	ClientCommand(Fmt( "clear;echo;echo;echo;echo\"----------------------------\";echo;echo %s;echo;echo\"Map: %s\";echo\"Tickrate: %g\";echo;showconsole;echo\"Time: %s\";echo;bench_end;echo;echo\"----------------------------\";echo;echo",
		( bAuto ? "Benchmark finished." :
		"Stopped benchmark." ),
		g_szMapName,
		g_flTickrate,
		szOutTime ));
	ClientCommand("developer " + m_iDev);

	if (bAuto) PlaySound("Buttons.snd9");
	PlaySound("UIPanorama.gameover_show");
}

function PostSpawn()
{
	if ( player.GetTeam() != 2 && player.GetTeam() != 3 )
		player.SetTeam(2);

	PlaySound("Player.DrownStart");

	// print after Steamworks Msg
	if ( GetDeveloperLevel() > 0 )
	{
		VS.EventQueue.AddEvent( ClientCommand, 0.75, [null, "clear;script _BM_.WelcomeMsg()"] );
	}
	else
	{
		VS.EventQueue.AddEvent( WelcomeMsg, 0.1, this );
	};
}

function WelcomeMsg()
{
	Msg("\n\n\n");
	Msg(Fmt( "   [v%s]     github.com/samisalreadytaken/csgo-benchmark\n", version ));
	Msg("\n");
	Msg("Console commands:\n");
	Msg("\n");
	Msg("benchmark  : Run benchmark\n");
	Msg("           :\n");
	Msg("bm_start   : Run benchmark (path only)\n");
	Msg("bm_stop    : Force stop ongoing benchmark\n");
	Msg("           :\n");
	Msg("bm_setup   : Print setup related commands\n");
	Msg("\n");
	Msg("----------\n");
	Msg("\n");
	Msg("Commands to display FPS:\n");
	Msg("\n");
	Msg("cl_showfps 1\n");
	Msg("net_graph 1\n");
	Msg("\n----------\n");
	Msg("\n");
	Msg(Fmt( "[i] Map: %s\n", g_szMapName ));
	Msg(Fmt( "[i] Server tickrate: %g\n", g_flTickrate ));
	Msg("\n");
	Msg("[i] The benchmark sets your fps_max to 0\n\n\n");

	if ( !VS.IsInteger( 128.0 / g_flTickrate ) )
	{
		Msg(Fmt( "[!] Invalid tickrate (%g)! Only 128 and 64 tickrates are supported.\n", g_flTickrate ));
		Chat(Fmt( "%s[!] %sInvalid tickrate ( %s%g%s )! Only 128 and 64 tickrates are supported.",
			TextColor.Red, TextColor.Normal, TextColor.Gold, g_flTickrate, TextColor.Normal ));
	};

	LoadData();

	if ( !ErrorCheck() )
		Msg("\n\n");
}

// bm_setup
function PrintSetupCmd()
{
	Msg("\n");
	Msg(Fmt( "   [v%s]     github.com/samisalreadytaken/csgo-benchmark\n", version ));
	Msg("\n");
	Msg("bm_timer   : Toggle counter\n");
	Msg("           :\n");
	Msg("bm_list    : Print saved setup data\n");
	Msg("bm_clear   : Clear saved setup data\n");
	Msg("bm_remove  : Remove the last added setup data\n");
	Msg("           :\n");
	Msg("bm_mdl     : Print and add to list SpawnMDL\n");
	Msg("bm_flash   : Print and add to list SpawnFlash\n");
	Msg("bm_he      : Print and add to list SpawnHE\n");
	Msg("bm_molo    : Print and add to list SpawnMolotov\n");
	Msg("bm_smoke   : Print and add to list SpawnSmoke\n");
	Msg("bm_expl    : Print and add to list SpawnExplosion\n");
	Msg("           :\n");
	Msg("bm_mdl1    : Spawn a playermodel\n");
	Msg("bm_flash1  : Spawn a flashbang\n");
	Msg("bm_he1     : Spawn an HE\n");
	Msg("bm_molo1   : Spawn a molotov\n");
	Msg("bm_smoke1  : Spawn smoke\n");
	Msg("bm_expl1   : Spawn a C4 explosion\n");
	Msg("\n");
	Msg("For creating camera paths, use the keyframes script.\n");
	Msg("                github.com/samisalreadytaken/keyframes\n\n\n");
}

// bm_clear
function ClearSetupData()
{
	PlaySound(SND_BUTTON);

	if ( m_list_models )
		m_list_models.clear();

	if ( m_list_nades )
		m_list_nades.clear();

	Msg("Cleared saved setup data.\n");
}

// bm_remove
function RemoveSetupData()
{
	PlaySound(SND_BUTTON);
	if ( !m_iRecLast )
	{
		if ( !m_list_models || !m_list_models.len() )
			return Msg("No saved data found.\n");

		m_list_models.pop();
		Msg("Removed the last added setup data. (model)\n");
	}
	else
	{
		if ( !m_list_nades || !m_list_nades.len() )
			return Msg("No saved data found.\n");

		m_list_nades.pop();
		Msg("Removed the last added setup data. (nade)\n");
	};
}

// bm_list
function ListSetupData()
{
	PlaySound(SND_BUTTON);

	if ( (!m_list_nades || !m_list_nades.len()) && (!m_list_models || !m_list_models.len()) )
		return Msg("No saved data found.\n");

	if ( !m_list_nades )
		m_list_nades = [];

	if ( !m_list_models )
		m_list_models = [];

	Msg( "//------------------------\n// Copy the lines below:\n\n\n" );
	Msg(Fmt( "function Setup_%s()\n{\n", g_szMapName ));
	foreach( k in m_list_models ) Msg(Fmt( "\t%s\n", k ));
	Msg("");
	foreach( k in m_list_nades ) Msg(Fmt( "\t%s\n", k ));
	Msg( "}\n\n" );
	Msg( "\n//------------------------\n" );
}

// bm_mdl
function PrintMDL( i = 0 )
{
	PlaySound(SND_BUTTON);

	local vecOrigin = player.GetOrigin();
	local out = Fmt( "SpawnMDL( %s,%g, MDL.ST6k )", VecToString( vecOrigin ), player.GetAngles().y );

	if (i)
	{
		vecOrigin.z += 72;
		player.SetOrigin(vecOrigin);
		return compilestring(out)();
	};

	if ( !m_list_models )
		m_list_models = [];

	m_list_models.append(out);
	Msg(Fmt( "\n%s\n", out ));
	m_iRecLast = 0;
}


const kSmoke     = 0;;
const kFlash     = 1;;
const kHE        = 2;;
const kMolotov   = 3;;
const kExplosion = 4;;


// bm_flash
function PrintFlash( i = 0 )
{
	PlaySound(SND_BUTTON);

	local vecOrigin = player.GetOrigin();
	vecOrigin.z += 4.0;

	if (i)
	{
		if ( !player.IsNoclipping() )
		{
			local t = Vector();
			VS.VectorCopy( vecOrigin, t );
			t.z += 32;
			player.SetOrigin(t);
		};
		return Dispatch( vecOrigin, kFlash );
	};

	if ( !m_list_nades )
		m_list_nades = [];

	local out = Fmt( "SpawnFlash( %s, 0.0 )", VecToString( vecOrigin ) );

	m_list_nades.append(out);
	Msg(Fmt( "\n%s\n", out ));
	m_iRecLast = 1;
}

// bm_he
function PrintHE( i = 0 )
{
	PlaySound(SND_BUTTON);

	local vecOrigin = player.GetOrigin();
	vecOrigin.z += 4.0;

	if (i)
	{
		if ( !player.IsNoclipping() )
		{
			local t = Vector();
			VS.VectorCopy( vecOrigin, t );
			t.z += 32;
			player.SetOrigin(t);
		};
		return Dispatch( vecOrigin, kHE );
	};

	if ( !m_list_nades )
		m_list_nades = [];

	local out = Fmt( "SpawnHE( %s, 0.0 )", VecToString( vecOrigin ) );

	m_list_nades.append(out);
	Msg(Fmt( "\n%s\n", out ));
	m_iRecLast = 1;
}

// bm_molo
function PrintMolo( i = 0 )
{
	PlaySound(SND_BUTTON);

	local vecOrigin = player.GetOrigin();
	vecOrigin.z += 4.0;

	if (i)
	{
		if ( !player.IsNoclipping() )
		{
			local t = Vector();
			VS.VectorCopy( vecOrigin, t );
			t.z += 32;
			player.SetOrigin(t);
		};
		return Dispatch( vecOrigin, kMolotov );
	};

	if ( !m_list_nades )
		m_list_nades = [];

	local out = Fmt( "SpawnMolotov( %s, 0.0 )", VecToString( vecOrigin ) );

	m_list_nades.append(out);
	Msg(Fmt( "\n%s\n", out ));
	m_iRecLast = 1;
}

// bm_smoke
function PrintSmoke( i = 0 )
{
	PlaySound(SND_BUTTON);

	local vecOrigin = player.GetOrigin();

	if (i)
		return Dispatch( vecOrigin, kSmoke );

	if ( !m_list_nades )
		m_list_nades = [];

	local out = Fmt( "SpawnSmoke( %s, 0.0 )", VecToString( vecOrigin ) );

	m_list_nades.append(out);
	Msg(Fmt( "\n%s\n", out ));
	m_iRecLast = 1;
}

// bm_expl
function PrintExpl( i = 0 )
{
	PlaySound(SND_BUTTON);

	local vecOrigin = player.GetOrigin();

	if (i)
		return Dispatch( vecOrigin, kExplosion );

	if ( !m_list_nades )
		m_list_nades = [];

	local out = Fmt( "SpawnExplosion( %s, 0.0 )", VecToString( vecOrigin ) );

	m_list_nades.append(out);
	Msg(Fmt( "\n%s\n", out ));
	m_iRecLast = 1;
}

function __Spawn( v, t ) : (Entities, EntFireByHandle, Vector)
{
	local ent;
	local vel = Vector(0,0,1);

	while ( ent = Entities.FindByClassname( ent, t ) )
	{
		ent.SetOrigin( v );
		ent.SetVelocity( vel );

		switch (t)
		{
			case "flashbang_projectile":
				EntFireByHandle( ent, "SetTimer", "0" );
				break;
			case "hegrenade_projectile":
			case "molotov_projectile":
				EntFireByHandle( ent, "InitializeSpawnFromWorld" );
				break;
		}
	}
}

function Dispatch( v, i ) :
	( ClientCommand, DispatchParticleEffect, Vector, VecToString )
{
	switch ( i )
	{
	case kSmoke:
		DispatchParticleEffect( "explosion_smokegrenade", v, Vector(1,0,0) );
		m_hHudHint.SetOrigin( v );
		m_hHudHint.EmitSound( "BaseSmokeEffect.Sound" );
		return;

	case kFlash:
		ClientCommand(Fmt( "ent_create flashbang_projectile\nscript _BM_.__Spawn(%s,\"flashbang_projectile\")", VecToString(v) ));
		return;

	case kHE:
		ClientCommand(Fmt( "ent_create hegrenade_projectile\nscript _BM_.__Spawn(%s,\"hegrenade_projectile\")", VecToString(v) ));
		return;

	case kMolotov:
		ClientCommand(Fmt( "ent_create molotov_projectile\nscript _BM_.__Spawn(%s,\"molotov_projectile\")", VecToString(v) ));
		return;

	case kExplosion:
		DispatchParticleEffect( "explosion_c4_500", v, Vector() );
		m_hHudHint.SetOrigin( v );
		m_hHudHint.EmitSound( "c4.explode" );
		return;
	}
}

function SpawnFlash( v, d )
{
	if ( m_bLooping && m_nPlaybackIdx )
		d -= 3.5;

	VS.EventQueue.AddEvent( Dispatch, d, [this,v,kFlash], null, player );
}

function SpawnHE( v, d )
{
	if ( m_bLooping && m_nPlaybackIdx )
		d -= 3.5;

	VS.EventQueue.AddEvent( Dispatch, d, [this,v,kHE], null, player );
}

function SpawnMolotov( v, d )
{
	if ( m_bLooping && m_nPlaybackIdx )
		d -= 3.5;

	VS.EventQueue.AddEvent( Dispatch, d, [this,v,kMolotov], null, player );
}

function SpawnSmoke( v, d )
{
	if ( m_bLooping && m_nPlaybackIdx )
		d -= 3.5;

	VS.EventQueue.AddEvent( Dispatch, d, [this,v,kSmoke], null, player );
}

function SpawnExplosion( v, d )
{
	if ( m_bLooping && m_nPlaybackIdx )
		d -= 3.5;

	VS.EventQueue.AddEvent( Dispatch, d, [this,v,kExplosion], null, player );
}

function SpawnMDL( v, a, m, p = 0 )
{
	if ( !Entities.FindByClassnameNearest( "prop_dynamic_override", v, 1 ) )
	{
		PrecacheModel( m );
		local h = CreateProp( "prop_dynamic_override", v, m, 0 );
		h.SetAngles( 0, a, 0 );
		h.__KeyValueFromInt( "solid", 2 );
		h.__KeyValueFromInt( "disablebonefollowers", 1 );
		h.__KeyValueFromInt( "holdanimation", 1 );
		h.__KeyValueFromString( "defaultanim", "grenade_deploy_03" );

		switch ( p )
		{
			case POSE.ROM:
				EntFireByHandle( h, "SetAnimation", "rom" );
				break;
			case POSE.A:
				h.SetAngles( 0, a + 90, 90 );
				EntFireByHandle( h, "SetAnimation", "additive_posebreaker" );
				break;
			case POSE.PISTOL:
				EntFireByHandle( h, "SetAnimation", "pistol_deploy_02" );
				break;
			case POSE.RIFLE:
				EntFireByHandle( h, "SetAnimation", "rifle_deploy" );
				break;
			default:
				EntFireByHandle( h, "SetAnimation", "grenade_deploy_03" );
				EntFireByHandle( h, "SetPlaybackRate", "0" );
		};
	};
}

function EntityAt( classname, pos, r = 1.0 )
{
	return Entities.FindByClassnameWithin( null, classname, pos, r );
}

}.call(_BM_);
