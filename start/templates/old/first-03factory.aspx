<%@ Page Title="" Language="C#" MasterPageFile="AutoWeightMaster.master" AutoEventWireup="true" CodeFile="first-03factory.aspx.cs" Inherits="stevedore_set_tranunits_shipper" %>

<asp:Content ID="ContentHeaders" ContentPlaceHolderID="StyleSelection" Runat="Server">

    <script type="text/javascript" id="telerikClientEvents1">
        function confirmAndClear() {
             if (confirm('OK?')) {
                 //clearButtonsRegion();
                 return true;
             }
             else {
                 return false;
             }
         }

    </script>

    <style type="text/css">
         .btn-xl {
             font-size: 50px;
         }
         .extrarow {
             padding-top: 50px;
         }
         .img-responsive {
                margin: 0 auto;
                    }

         input[type=text] {
          background-color: #ffffe6;
        }

        input[type=text]:focus {
          background-color: #e6ffe6;
        }

        div.PagerLeft_MyDefault{ float:right;}
    div.PagerRight_MyDefault{
    clear: right;}

     .extraspace {
             padding-top: 150px;
         }
        </style>

</asp:Content>

<asp:Content ID="ContentMain" ContentPlaceHolderID="ContentSection" Runat="Server">

    


    <asp:SqlDataSource ID="dSfactorys" runat="server" ConnectionString="<%$ ConnectionStrings:conAgency %>" 
        SelectCommand="SELECT DISTINCT Company_1.CompanyID AS factoryNameID, ' ' + Company_1.name AS factoryName FROM TranunitLists INNER JOIN Tranunits ON TranunitLists.shipperId = Tranunits.shipperId INNER JOIN Company ON TranunitLists.shipperId = Company.CompanyID LEFT OUTER JOIN Company AS Company_1 ON Tranunits.factoryId = Company_1.CompanyID WHERE ((TranunitLists.name LIKE N'%190808%') OR (TranunitLists.name LIKE N'%190809%')) AND Company_1.name &lt; 'm' ORDER BY factoryName" 
        >
    </asp:SqlDataSource>


    <telerik:RadAjaxManagerProxy ID="RadAjaxManagerProxy1" runat="server">
        <AjaxSettings>
           
            <telerik:AjaxSetting AjaxControlID="gDfactorysFirst">
                <UpdatedControls>
                    <telerik:AjaxUpdatedControl ControlID="pLfactorysMiddle" UpdatePanelCssClass="" />
                    <telerik:AjaxUpdatedControl ControlID="pLfactorysLast" UpdatePanelCssClass="" />
                    <telerik:AjaxUpdatedControl ControlID="pLproceed" UpdatePanelCssClass="" />
                </UpdatedControls>
            </telerik:AjaxSetting>
           
            <telerik:AjaxSetting AjaxControlID="gDfactorysMiddle">
                <UpdatedControls>
                    <telerik:AjaxUpdatedControl ControlID="pLfactorysFirst" UpdatePanelCssClass="" />
                    <telerik:AjaxUpdatedControl ControlID="pLfactorysLast" UpdatePanelCssClass="" />
                    <telerik:AjaxUpdatedControl ControlID="pLproceed" UpdatePanelCssClass="" />
                </UpdatedControls>
            </telerik:AjaxSetting>
            <telerik:AjaxSetting AjaxControlID="gDfactorysLast">
                <UpdatedControls>
                    <telerik:AjaxUpdatedControl ControlID="pLfactorysFirst" UpdatePanelCssClass="" />
                    <telerik:AjaxUpdatedControl ControlID="pLfactorysMiddle" UpdatePanelCssClass="" />
                    <telerik:AjaxUpdatedControl ControlID="pLproceed" UpdatePanelCssClass="" />
                </UpdatedControls>
            </telerik:AjaxSetting>
           
        </AjaxSettings>
        </telerik:RadAjaxManagerProxy>

    <div class="container-fluid text-center">
      <!-- Main component for a primary marketing message or call to action -->
                 
            <div class="row" >
                 <div class="col-md-12">   
                             <h4><asp:Literal ID="instructionText" runat="server">
                                 </asp:Literal>
                                 </h4>
                  </div>          
             </div>
            <div class="row">
                
                <asp:Panel ID="pLfactorysFirst" CssClass="col-sm-4" runat="server">
               
                     <telerik:RadGrid ID="gDfactorysFirst" 
                         runat="server" 
                         EnableLinqExpressions="False" AllowSorting="True" AutoGenerateColumns="False" GroupPanelPosition="Top"
                        Skin="Bootstrap" PageSize="12" 
                        CellSpacing="-1" GridLines="Both" 
                         OnSelectedIndexChanged="gDfactorysFirst_SelectedIndexChanged" AllowFilteringByColumn="True" PagerStyle-CssClass="PagerRight_MyDefault" ShowHeader="False">
<GroupingSettings CollapseAllTooltip="Collapse all groups" CaseSensitive="False" ></GroupingSettings>
                        <ExportSettings ExportOnlyData="True" IgnorePaging="True">
                            <Excel Format="Xlsx" />
                        </ExportSettings>
                         <ClientSettings EnablePostBackOnRowClick="True">
                            <Selecting AllowRowSelect="True" />
                             </ClientSettings>
                        <MasterTableView DataKeyNames="factoryNameID"  
                            
                            NoMasterRecordsText="" 
                            >
                            <CommandItemSettings AddNewRecordText="Добавить новое ТС" ShowExportToExcelButton="False"  />
                            <RowIndicatorColumn Visible="False">
                                <HeaderStyle Width="41px" />
                            </RowIndicatorColumn>
                            <ExpandCollapseColumn Created="True">
                                <HeaderStyle Width="41px" />
                            </ExpandCollapseColumn>
                            <Columns>
                                <telerik:GridBoundColumn DataField="factoryNameID" 
                                    DataType="System.Int32" 
                                    FilterControlAltText="Filter factoryNameID column" 
                                    HeaderText="factoryNameID" ReadOnly="True" Visible="false"
                                    SortExpression="factoryNameID" UniqueName="factoryNameID">
                                </telerik:GridBoundColumn>
                                <telerik:GridBoundColumn DataField="factoryName" 
                                    FilterControlAltText="Filter factoryName column" 
                                    HeaderText="Nosūtītājs/хозяйство" 
                                    ReadOnly="True" SortExpression="factoryName" UniqueName="factoryName">
                                </telerik:GridBoundColumn>
                            </Columns>


                        </MasterTableView>
                         <PagerStyle Font-Size="X-Large" PageSizeControlType="None"
                             HorizontalAlign="Right" Position="TopAndBottom" />
                    </telerik:RadGrid>
 
                </asp:Panel>

                <asp:Panel ID="pLfactorysMiddle" CssClass="col-sm-4" runat="server">
               
                     <telerik:RadGrid ID="gDfactorysMiddle" 
                         
                         runat="server" EnableLinqExpressions="False" AllowSorting="True" AutoGenerateColumns="False" GroupPanelPosition="Top"
                        Skin="Bootstrap" PageSize="12" 
                        CellSpacing="-1" GridLines="Both" 
                         OnSelectedIndexChanged="gDfactorysMiddle_SelectedIndexChanged" AllowFilteringByColumn="True" PagerStyle-CssClass="PagerRight_MyDefault" ShowHeader="False">
<GroupingSettings CollapseAllTooltip="Collapse all groups" CaseSensitive="False" ></GroupingSettings>
                        <ExportSettings ExportOnlyData="True" IgnorePaging="True">
                            <Excel Format="Xlsx" />
                        </ExportSettings>
                         <ClientSettings EnablePostBackOnRowClick="True">
                            <Selecting AllowRowSelect="True" />
                             </ClientSettings>
                        <MasterTableView DataKeyNames="factoryNameID"  
                             
                            NoMasterRecordsText="" 
                            >
                            <CommandItemSettings AddNewRecordText="Добавить новое ТС" ShowExportToExcelButton="False"  />
                            <RowIndicatorColumn Visible="False">
                                <HeaderStyle Width="41px" />
                            </RowIndicatorColumn>
                            <ExpandCollapseColumn Created="True">
                                <HeaderStyle Width="41px" />
                            </ExpandCollapseColumn>
                            <Columns>
                                <telerik:GridBoundColumn DataField="factoryNameID" 
                                    DataType="System.Int32" 
                                    FilterControlAltText="Filter factoryNameID column" 
                                    HeaderText="factoryNameID" ReadOnly="True" Visible="false"
                                    SortExpression="factoryNameID" UniqueName="factoryNameID">
                                </telerik:GridBoundColumn>
                                <telerik:GridBoundColumn DataField="factoryName" 
                                    FilterControlAltText="Filter factoryName column" 
                                    HeaderText="Nosūtītājs/хозяйство" 
                                    ReadOnly="True" SortExpression="factoryName" UniqueName="factoryName">
                                </telerik:GridBoundColumn>
                            </Columns>


                        </MasterTableView>
                         <PagerStyle Font-Size="X-Large" PageSizeControlType="None"
                             HorizontalAlign="Right" Position="TopAndBottom" />
                    </telerik:RadGrid>
 
                </asp:Panel>

                <asp:Panel ID="pLfactorysLast" CssClass="col-sm-4" runat="server">
               
                     <telerik:RadGrid ID="gDfactorysLast" 
                         
                         runat="server" EnableLinqExpressions="False" AllowSorting="True" AutoGenerateColumns="False" GroupPanelPosition="Top"
                        Skin="Bootstrap" PageSize="12" 
                        CellSpacing="-1" GridLines="Both" 
                         OnSelectedIndexChanged="gDfactorysLast_SelectedIndexChanged" AllowFilteringByColumn="True" PagerStyle-CssClass="PagerRight_MyDefault" ShowHeader="False">
<GroupingSettings CollapseAllTooltip="Collapse all groups" CaseSensitive="False" ></GroupingSettings>
                        <ExportSettings ExportOnlyData="True" IgnorePaging="True">
                            <Excel Format="Xlsx" />
                        </ExportSettings>
                         <ClientSettings EnablePostBackOnRowClick="True">
                            <Selecting AllowRowSelect="True" />
                             </ClientSettings>
                        <MasterTableView DataKeyNames="factoryNameID"  
                            
                            NoMasterRecordsText="Lūdzu, jautājiet palīdzību no stividora. 
                            Обращайтесь за помощью к стивидору." 
                            >
                            <CommandItemSettings AddNewRecordText="Добавить новое ТС" ShowExportToExcelButton="False"  />
                            <RowIndicatorColumn Visible="False">
                                <HeaderStyle Width="41px" />
                            </RowIndicatorColumn>
                            <ExpandCollapseColumn Created="True">
                                <HeaderStyle Width="41px" />
                            </ExpandCollapseColumn>
                            <Columns>
                                <telerik:GridBoundColumn DataField="factoryNameID" 
                                    DataType="System.Int32" 
                                    FilterControlAltText="Filter factoryNameID column" 
                                    HeaderText="factoryNameID" ReadOnly="True" Visible="false"
                                    SortExpression="factoryNameID" UniqueName="factoryNameID">
                                </telerik:GridBoundColumn>
                                <telerik:GridBoundColumn DataField="factoryName" 
                                    FilterControlAltText="Filter factoryName column" 
                                    HeaderText="Nosūtītājs/хозяйство" 
                                    ReadOnly="True" SortExpression="factoryName" UniqueName="factoryName">
                                </telerik:GridBoundColumn>
                            </Columns>


                        </MasterTableView>
                         <PagerStyle Font-Size="X-Large" PageSizeControlType="None"
                             HorizontalAlign="Right" Position="TopAndBottom" />
                    </telerik:RadGrid>
 
                </asp:Panel>
               
            <!-- /container -->
          </div> <!-- maun row -->
        <div class="row extrarow">
            <div class="col-sm-12">
                <div class="row">
                 <asp:Panel ID="pLproceed" Visible="false" CssClass="col-sm-12" runat="server" 
                     style="background-color:#f9fbff;">
             
             
                           <asp:Literal ID="chosenFactoryText" runat="server">
                                 </asp:Literal>

                                 <h4>
                                     <asp:Label ID="lLselectedFactory" runat="server" Text=""></asp:Label>
                                 </h4>
                 
                 
                          <asp:HyperLink ID="hLproceed" CssClass=" btn btn-success" Font-Size="XX-Large" runat="server">
                              
                              
                              <asp:Literal ID="goButtonText" runat="server">
                                 </asp:Literal>

                          </asp:HyperLink>
             
                
                    </asp:Panel>
                </div>
               <div class="row extrarow">
                         <div class="col-md-12 extrarow text-right">
                             </div>
                   </div>
                    <div class="row extrarow">
                         <div class="col-md-12 extrarow text-right">
                                 

                              <asp:HyperLink ID="hLgoBack" CssClass=" btn btn-danger" runat="server">

                                  <asp:Literal ID="backButtonText" runat="server">
                                 </asp:Literal>

                                   </asp:HyperLink>
                         </div>
               
                    </div>
                </div>

        </div> <%--button row--%>


    </div> <!-- /container -->

</asp:Content>
<asp:Content ID="ScripsContent" ContentPlaceHolderID="ScriptSection" Runat="Server">

    <script>

  

    $(".numbersonly").keypress(function (e) {
    //if the letter is not digit then display error and don't type anything
    if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
    //display error message
    // alert("Insert Only Numbers");
    return false;
    }
    });

    
</script>

</asp:Content>

