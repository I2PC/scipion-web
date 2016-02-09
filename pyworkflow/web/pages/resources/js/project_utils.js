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
/******************************************************************************
 * DESCRIPTION:
 * 
 * Methods used in the project template
 * 
 * ATTRIBUTES LIST:
 * 
 * METHODS LIST:
 * 
 * function createProjectForm()
 * 	->	Dialog web form based in messi.js to verify the option to create a project.
 * 		A name for the project is asked. 
 * 
 * function createProjectFromPopup(elm)
 *  ->	Method to call createProject receiving element from the popup (input from the user)
 *  
 * function createProject(projectName, workflow)
 *  ->	Method to execute the creation for a project.
 *
 * function deleteProjectForm(projName)
 *  ->	Dialog web form based in messi.js to verify the option to delete a project.
 *  
 * function deleteProject(elm)
 *  ->	Method to execute a delete for a project.
 * 
 ******************************************************************************/

 /** METHODS ******************************************************************/

/*
 * PROJECTS
 */

function createProjectForm(title, msg) {
	var msg = msg +"<input type='text' id='newProjName' class='content'/>";
	if (workflows !== undefined && workflows.length > 0){

		var workflowsForm = "<br/>";

		workflowsForm += "<label for='workflow'>Template: </label>";
		workflowsForm += "<select id='workflow' name='workflow' class='content' style='float: right; width: 59%;'>";
			workflowsForm += "<option value=''>None</option>";

			for (var index in workflows){
				var workflow = workflows[index];
				workflowsForm += "<option value='" + workflow.file + "'>" + workflow.name + "</option>";
			}

		workflowsForm += "</select>";
		msg += workflowsForm;
	}

	var funcName = 'createProjectFromPopup';
	warningPopup(title, msg, funcName);
}

 function createProjectFromPopup(elm) {
	var projName = elm[0].value;
 	var workflow = elm[1].value;

 	createProject(projName, workflow);
 }

function createProject(projectName, workflow) {

	var URL = getSubDomainURL() + "/create_project/?p=" + projectName

	if (workflow != '') {
		URL += '&w=' + workflow;
	}

	$.ajax({
		type : "GET",
		url : URL,
		success : function() {
			var URL2 = getSubDomainURL() + "/project_content/?p="+projectName
			window.location.href = URL2;
		}
	});
}

function deleteProjectForm(projName, title, dialog) {
	var title = 'Confirm DELETE project ' + projName 
	var msg = "<td class='content' value='"	+ projName +"'>"
			+ dialog 
			+ "</td>";
			
	var funcName = 'deleteProject';
	
	warningPopup(title, msg, funcName);
}

function deleteProject(elm) {
	var projName = elm.attr('value');
	var URL = getSubDomainURL() + "/delete_project/?p=" + projName
	$.ajax({
		type : "GET",
		url : URL,
		success : function() {
			var URL2 = getSubDomainURL() + "/projects/"
			window.location.href = URL2;
		}
	});
}
