//-----------------------------------------------------------------------
//             github.com/samisalreadytaken/csgo-benchmark
//-----------------------------------------------------------------------
//
// This file is an additional way to load map data.
// If no data from 'bm_mapname.nut' file is found, this file is checked for
// 'bm_mapname' motion data and 'Setup_mapname()' setup function.
//
// While testing the timings to determine when to spawn grenades,
// execute 'benchmark;bm_timer' in the console to start the timer.
//
// Use the commands to get setup lines
//    bm_mdl
//    bm_flash
//    bm_he
//    bm_molo
//    bm_smoke
//    bm_expl
//
// Use bm_list to print every saved line
//
// Restarting the round (mp_restartgame 1) will remove spawned models
//
/*
enum MDL
{
	FBIa, FBIb, FBIc, FBId, FBIe, FBIf, FBIg, FBIh,
	GIGNa, GIGNb, GIGNc, GIGNd,
	GSG9a, GSG9b, GSG9c, GSG9d,
	IDFb, IDFc, IDFd, IDFe, IDFf,
	SASa, SASb, SASc, SASd, SASe, SASf,
	ST6a, ST6b, ST6c, ST6d, ST6e, ST6g, ST6i, ST6k, ST6m,
	SWATa, SWATb, SWATc, SWATd,
	ANARa, ANARb, ANARc, ANARd,
	BALKa, BALKb, BALKc, BALKd, BALKe, BALKf, BALKg, BALKh, BALKi, BALKj,
	LEETa, LEETb, LEETc, LEETd, LEETe, LEETf, LEETg, LEETh, LEETi,
	PHXa, PHXb, PHXc, PHXd, PHXf, PHXg, PHXh,
	PRTa, PRTb, PRTc, PRTd,
	PROa, PROb, PROc, PROd,
	SEPa, SEPb, SEPc, SEPd,
	H_CT, H_T
}

enum POSE
{
	DEFAULT,
	ROM,
	A,
	PISTOL,
	RIFLE
}
*/

//---------------

