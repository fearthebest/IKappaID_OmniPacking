# Optional addon — Skill Book Expansion

Workshop: [3557111695](https://steamcommunity.com/sharedfiles/filedetails/?id=3557111695) (`SkillBookExpansionB42`)

**Mod ID:** `IKappaIDOmniPacking_SkillBookExpansion`

Load order (top → bottom):

1. Skill Book Expansion  
2. IKappaID's Omni Packing  
3. IKappaID's Omni Packing — Skill Book Expansion  

Regenerate addon scripts:

```powershell
python Things for-from Cursor\IKappaIDOmniPacking\scripts\generate_scripts_sbe.py
```

Then `sync_to_workshop.ps1` (copies main + addon into one Workshop `Contents/mods/` tree).
