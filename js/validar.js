function parse_ale(ale, loctrue, locfalse){
    if (ale.split("|")[0]=="True"){
        if (ale.split("|")[1]==null){
            alert(ale.split("|")[1]);
        }
        if (loctrue!=""){
            location=loctrue;
        }
    }else if(ale.split("|")[0]=="False"){
        if (ale.split("|")[1]!=null){
            alert(ale.split("|")[1]);
        }
        if (locfalse!=""){
            location=locfalse;
        }
    }else if(ale.split("|")[0]=="Logout"){
        if (ale.split("|")[1]!=null){ 
            alert(ale.split("|")[1]);
        }
        if (locfalse!=""){
            location="index.psp"; 
        }
    }
}

function isFloat(number, name){
    resultado=true;    
    if (!/^[-+]?[0-9]+(\.[0-9]+)?$/.test(number)){
        alert("El "+name+" no es un número decimal");
        resultado=false;
    }
    return resultado;
}
