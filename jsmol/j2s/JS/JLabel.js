Clazz.declarePackage("JS");
Clazz.load(["JS.JComponent"], "JS.JLabel", ["JU.SB"], function(){
var c$ = Clazz.declareType(JS, "JLabel", JS.JComponent);
Clazz.makeConstructor(c$, 
function(text){
Clazz.superConstructor(this, JS.JLabel, ["lblJL"]);
this.text = text;
}, "~S");
Clazz.overrideMethod(c$, "toHTML", 
function(){
var sb =  new JU.SB();
sb.append("<span id='" + this.id + "' class='JLabel' style='" + this.getCSSstyle(0, 0) + "'>");
sb.append(this.text);
sb.append("</span>");
return sb.toString();
});
});
;//5.0.1-v7 Thu May 08 14:17:10 CDT 2025
