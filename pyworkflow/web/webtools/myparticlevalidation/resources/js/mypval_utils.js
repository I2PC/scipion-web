 /*****************************************************************************
 *
 * Authors:    Jose Gutierrez (jose.gutierrez@cnb.csic.es)
 *
 * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 * 02111-1307  USA
 *
 *  All comments concerning this program package may be sent to the
 *  e-mail address 'jmdelarosa@cnb.csic.es'
 *
 ******************************************************************************/

function serviceProjForm(){
	var title = 'Project creation'
	var dialog = "<p>Your <strong>Project</strong> will be created.<br /><br />" +
        "This process generates a unique <strong>url access</strong>.<br /><br />" +
        "This url access should be used to have access to your data in future sessions.</p>" +
        "<p><br /></p>";
	
    dialog += "<p>Confirm to generate it.</p>";

	var funcName = 'createPvalProject';

	accessPopup(title, dialog, funcName, 'Confirm', 'Cancel');
}

function serviceTestDataForm(){
	var title = 'Test data'
		var dialog = ""
			
		dialog += "<p><strong>Create a project</strong> with <strong>Test data</strong> already imported inside.<br /></p>";
		dialog += "<br />";
		dialog += '<div id="testData">';
		dialog += "<p>Select <strong>Test data</strong>:</p>";
		dialog += '&nbsp;&nbsp;&nbsp;<input type="radio" name="data" value="betagal" checked>';
		dialog += '&nbsp;&nbsp;' + getRefTestData("betagal");
		dialog += '<br />';
		dialog += '&nbsp;&nbsp;&nbsp;<input type="radio" name="data" value="10004" checked>';
		dialog += '&nbsp;&nbsp;' + getRefTestData("10004");
		dialog += '<br />';
		dialog += '&nbsp;&nbsp;&nbsp;<input type="radio" name="data" value="10008" checked>';
		dialog += '&nbsp;&nbsp;' + getRefTestData("10008");
		dialog += '<br />';

		dialog += "</div>";
		dialog += "<br />";

	    
	    var btn1 = 'Create project'
		var ico1 = 'fa-check'
		var funcName1 = 'createPvalProject';
		
	    accessPopup(title, dialog, funcName1, btn1, "Cancel")
}

function goExampleForm(){
	var title = 'Example projects'
	var dialog = ""

	dialog += '<div id="exProjects">';
	dialog += "<p>Select the <strong>Test data</strong>:</p>";
	dialog += '&nbsp;&nbsp;&nbsp;<input type="radio" name="data" value="betagal" checked>';
	dialog += '&nbsp;&nbsp;' + getRefTestData("betagal");
	dialog += '<br />';
	dialog += '&nbsp;&nbsp;&nbsp;<input type="radio" name="data" value="10004" checked>';
	dialog += '&nbsp;&nbsp;' + getRefTestData("10004");
	dialog += '<br />';
	dialog += '&nbsp;&nbsp;&nbsp;<input type="radio" name="data" value="10008" checked>';
	dialog += '&nbsp;&nbsp;' + getRefTestData("10008");
	dialog += '<br />';
	dialog += "</div>";
	dialog += "<br />";
	
	accessPopup(title, dialog, 'getProjExample', 'Go to project', 'Cancel');
		
}

function getProjExample(elm){
	var x = $("div#exProjects input[type='radio']:checked").val();
	switch(x){
		case "betagal":
			var url = "/p_content?p=betagal";
			break;
		case "10004":
			var url = "/p_content?p=empiar10004";
			break;
		case "10008":
			var url = "/p_content?p=empiar10008";
			break;

	}
	goWithSubDomainURL(url);
}


function createPvalProject(elm) {
	var projName = "pval"+randomString(16, '#aA')
	var selected = $("#testData input[type='radio']:checked").val();

	var projectUrl = getBaseURL() + "/p_content?p="+ projName
	var URL = getSubDomainURL() + "/create_pval_project/?p=" + projName
	if(selected != undefined){
		URL += "&testData="+selected;
	}
	
	$.ajax({
		type : "GET",
		url : URL,
		async : false,
		success : function() {
			var title = "ACCESS CODE"
			
			var msg = "<p>Your <strong>url to access </strong> this <strong>Project</strong> is:</p>" +
			"<br /><p><h3>" + 
			"<a style='color:firebrick;' href='"+ projectUrl + "'>" +
			projectUrl + "</a>"+
			"</h3></p><br />" +
			"<p>The access to this project will be <strong>DELETED TWO WEEKS</strong> after its creation.</p><br />"+
            "<p>Please <strong>SAVE or BOOKMARK this url securely</strong> " +
			"in order to access this project in future sessions.</p>"+
			"<p>If you experience any problem contact us on this email: <span style='color:firebrick;'>scipion at cnb.csic.es</span></p>";
			
			msg = msg + "<input type='hidden' class='content' value='" + projName + "' />";
			var funcName = "goToProject"

			accessPopup(title, msg, funcName, 'Go to the project', 'Exit');
		}
	});
}

function goToProject(elm) {
	var code = elm.val();
	var URL2 = getSubDomainURL() + "/p_content?p="+code;
	window.location.href = URL2;
}

function getRefTestData(id){
	var ref = ""
	switch(id){
		case "betagal":
			ref = "<strong>β-galactosidase</strong> (<a href='http://dx.doi.org/10.1016%2Fj.str.2014.01.011' style='color:firebrick;' target='_blank'>from Vinothkumar et al. Cell PRESS, 2014</a>)"
			break;
		case "10004":
			ref = "<strong>HIV-1 envelope glycoprotein (Empiar 10004)</strong> (<a href='http://dx.doi.org/10.1038/nsmb.2711' style='color:firebrick;' target='_blank'>from Bartesaghi et al. Nature Structural & Molecular Biology, 2013</a>)"
			break;
		case "10008":
			ref = "<strong>HIV-1 envelope glycoprotein (Empiar 10008)</strong> (<a href='http://dx.doi.org/10.1073/pnas.1307382110' style='color:firebrick;' target='_blank'>from Mao et al. PNAS, 2013</a>)"
			break;

	}
	return ref;
}
