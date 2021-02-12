# Agenda for Future Development

## Direction and Distance
  * output by default is "remaining fields"  can this be changed?
  * add information that the distance calculation is ellipsoidal using the WGS 1984 geographic coordinate system and that the direction calculation is calculated on the world mercator projected coordinate system.
  * this is great! as far as I can tell, this gives accurate results even if the user is selecting multiple polygons as the "origin" and if the origin and input features are using different incorrect CRSs!
  
## Group By
  * output by default is "SQL Output" can this be changed?
  * document that all outputs get a featCount field counting the number of features in each group
  * can output be forced to be a table?  Or should we just in the long-term have a table-only version of this that can also take a table as input?
  * not possible to run tool with "selected features only" option -- cannot find INPUT layer. This actually seems to be a limitation of the Execute SQL tool: it seems like it will only run for a whole layer. For now, perhaps the tool should accept only a layer, not a set of features.
  * this is also great!  Works in almost all cases I tested.
