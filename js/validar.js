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

function isFloat(number, ale){
    var resultado=true;    
    if (!/^[-+]?[0-9]+(\.[0-9]+)?$/.test(number)){
        alert(ale);
        resultado=false;
    }
    return resultado;
}


function isISODate(date, ale){
    var resultado=true;    
    if (!/^[0-9][0-9][0-9][0-9](-[0-1][0-9](-[0-3][0-9](T[0-9][0-9](:[0-9][0-9](:[0-9][0-9])?)?)?)?)?$/.test(date)){
        alert(ale);
        resultado=false;
    }
    return resultado;
}

function isStringBD(s, ale){
    var resultado=true;
    if (s==null){
        return true
    }
    //Comprueba si tiene comillas
    if (/[\'\"]/.test(s)){
        alert(ale);
        resultado=false;
    }   
    return resultado;
}
