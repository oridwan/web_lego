Clazz.declarePackage("JS");
Clazz.load(["JS.Container"], "JS.JComponent", null, function(){
var c$ = Clazz.decorateAsClass(function(){
this.autoScrolls = false;
this.actionCommand = null;
this.actionListener = null;
Clazz.instantialize(this, arguments);}, JS, "JComponent", JS.Container);
Clazz.defineMethod(c$, "setAutoscrolls", 
function(b){
this.autoScrolls = b;
}, "~B");
Clazz.defineMethod(c$, "addActionListener", 
function(listener){
this.actionListener = listener;
}, "~O");
Clazz.defineMethod(c$, "getActionCommand", 
function(){
return this.actionCommand;
});
Clazz.defineMethod(c$, "setActionCommand", 
function(actionCommand){
this.actionCommand = actionCommand;
}, "~S");
});
;//5.0.1-v7 Thu May 08 14:17:10 CDT 2025
