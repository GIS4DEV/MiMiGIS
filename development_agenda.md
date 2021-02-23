# Agenda for Future Development

## Direction and Distance
  * output by default is "remaining fields"  can this be changed? *see below*
  * this is great! as far as I can tell, this gives accurate results even if the user is selecting multiple polygons as the "origin" and if the origin and input features are using different incorrect CRSs!

## Group By
  * output by default is "SQL Output" can this be changed? *see below*
  * can output be forced to be a table?  Or should we just in the long-term have a table-only version of this that can also take a table as input? The best move might be a dissolved variant of this tool which always dissolves and must have a geometry input, and a table variant of this which always saves as simple tables and can accept tabular inputs.
  * not possible to run tool with "selected features only" option -- cannot find INPUT layer. This actually seems to be a limitation of the Execute SQL tool: it seems like it will only run for a whole layer. For now, perhaps the tool should accept only a layer, not a set of features. Or, it need to be able to trick the Execute SQL tool into thinking it has a whole layer, e.g. maybe by throwing the "extract selected features" into the mix if any features are in fact selected.
  * this is also great!  Works in almost all cases I tested.

## Network Analysis
  * Could QGIS implement the networkX package for Network analysis? https://github.com/tomasholderness/NetworkX-Tools-QGIS-Plugin This could be so much more efficient than QNEAT3

## Rename default output layer names if the output is a temporary layer
Maja: After reading through a number of GIS Stack Exchange discussions, I came to the unfortunate conclusion that there’s no straightforward solution if we want the user to have the option to either save the layer to a file or get a temporary output. A lot of other people have had similar issues (the layer name was good when they ran their model, but once they converted to a Python script the layer just took the name of the last tool) and have not been able to find good solutions. The main consensus seemed to be that you would need to copy all the features to a new feature sink (or something along those lines), and one person even said they were using an external script to do that. So I guess the short answer is it might be possible, but it might also be a lot of work and a bit confusing. Given that the output name issue is annoying but doesn’t impact the actual results of the algorithms, my instinct would be to keep that on the “another project for another day” list—what do you think? It would be easier to fix this if we were just doing a non-Processing script that handled the map layers as well as tool execution, but it seems like using the Processing framework forces one to give up some control over how layers arrive on the map.

## Allow 'selected features only' to be used as input features
Maja: Like we had already figured out, the `Execute SQL` tool doesn’t want to accept anything but a layer as its input parameter. So I tried to change the format of the input layer, which was ultimately unsuccessful, and then I tried to run the layer through a dummy tool (I tried Random Extract with 100% of features) to get it into a better format. If I didn’t select any group or summary fields, the query worked. However, I started getting problems when I used group/summary fields because the Execute SQL input was a virtual layer and the tool was unable to access the fields in that layer by name for some reason, even though the fields were all there. I tried to find a solution, but nothing seemed to work. 
