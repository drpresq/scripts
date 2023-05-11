<#

Someone on the Facebook group asked if there was an automated way to pull ATCTS reports.  I got a wild hair and made one.

This PowerShell script connects to ACTCS and pulls down a copy of the report of your choosing to your default download location.

**Open in PowerShell ISE**

**You must edit the script prior to using it:

	1) You must add the tail of the URL to your target report from the ATCTS site.

	2) You must add the tail of the URL to the 'export this report' link from your target report.


**Note**

The script does not work when PowerShell is operating in Constrained Language Mode.

It won't tell you that's the problem you'll just get errors as the script tries to interact with the Internet Explorer COM Object that gets wiped out as soon as it navigates to ATCTS.

You can verify your language mode by opening PowerShell and typing:

	$ExecutionContext.SessionState.LanguageMode

You'll need to avoid constrained language mode in order for it to work. Your methods for doing so are your own. Don't violate any Acceptable Use Policies.

#>


function login-atctsomatic(){
[cmdletbinding()]
    Param(
        [parameter(Mandatory=$true)]$Browser
    )
       
    Begin{}

    Process{
        $Browser.navigate("https://atc.us.army.mil")
        Do{Start-Sleep -s 2}Until(!($Browser.Busy))
        if($Browser.locationurl -match "federation\.eams\.army\.mil"){
            ($Browser.Document.getElementById("pki-login")).click()
            Do{Start-Sleep -s 2}Until(!($Browser.Busy))
        }
        ($Browser.Document.body.getElementsByTagName("A") | Where-Object {$_.nameprop -match "login.php"}).click()
        Do{Start-Sleep -s 2}Until(!($Browser.Busy))
        ($Browser.document.body.getElementsByTagName("input")| Where-Object {$_.id -match "dod_accept"}).click()
        Do{Start-Sleep -s 2}Until(!($Browser.Busy))
        ($Browser.document.body.getElementsByTagName("input"))[1].click()
        Do{Start-Sleep -s 2}Until(!($Browser.Busy))
    }

    End{
        return
    }
}

function DownloadReport-AtctsOmatic(){
[cmdletbinding()]
    Param(
        [parameter(Mandatory=$true)]$Browser,
        [parameter(Mandatory=$true)]$ReportUri,
        [parameter(Mandatory=$true)]$DownloadUri
    )

    Begin{}

    Process{
        ($Browser.Document.body.getElementsByTagName("A") | Where-Object {$_.nameprop -match "management.php"}).click()
        Do{Start-Sleep -s 2}Until(!($Browser.Busy))
        ($Browser.Document.body.getElementsByTagName("A") | Where-Object {$_.nameprop -match "unit_reports.php"}).click()
        Do{Start-Sleep -s 2}Until(!($Browser.Busy))
        ($Browser.Document.body.getElementsByTagName("A") | Where-Object {$_.nameprop -match "report_load.php"}).click()
        Do{Start-Sleep -s 2}Until(!($Browser.Busy))
        ($Browser.Document.body.getElementsByTagName("A") | Where-Object {$_.nameprop -match $ReportUri}).click()
	Do{Start-Sleep -s 2}Until(!($Browser.Busy))
        $Browser.visible = $true
        $win = Add-Type -Name win -MemberDefinition @"
[DllImport("user32.dll")]
[return: MarshalAs(UnmanagedType.Bool)]
public static extern bool SetForegroundWindow(IntPtr hWnd);
"@ -Passthru
        $win::SetForegroundWindow($Browser.HWND)
        Do{Start-Sleep -s 2}Until(!($Browser.Busy))
        ($Browser.Document.body.getElementsByTagName("A") | Where-Object {$_.nameprop -match $DownloadUri}).click()
        Do{Start-Sleep -s 2}Until(!($Browser.Busy))
        [void][System.Reflection.Assembly]::LoadWithPartialName("'System.Windows.Forms")
        [System.Windows.Forms.SendKeys]::SendWait("%")
        Do{Start-Sleep -s 2}Until(!($Browser.Busy))
        [System.Windows.Forms.SendKeys]::SendWait("%s")
        Do{Start-Sleep -s 2}Until(!($Browser.Busy))
        $Browser.visible = $false
    }

    End{
        Return
    }
}

 

Write-Host @"

*******************************************************************

OPEN THIS IN THE POWERSHELL ISE FIRST!

YOU MUST EDIT THE SCRIPT BEFORE RUNNING IT!

*******************************************************************

"@

 

#region Instructions
<#

1) Change the text in the double quotes on the lines that are marked 'change me'
    in the 'Make Changes Here!' region below

2) Go to the ATCTS website > management > reports > load a custom report
    grab the link for the custom report you want to download and place it in ReportUri below

3) Do the same thing for the 'export this report link' on your target custom report

#>
#endregion

 

#region Make Changes Here!

$ReportVars = @{
    Browser = $ie
    ReportUri = "report_load.php\?id\=114499\&unit_id\=22413\&tree\=1\&w\=m" #change me
    DownloadUri = "report_display.php\?1\&w\=m\&unit_id\=22413\&tree\=1\&rep\=session\&output\=csv" #change me
}

#endregion

 

#region Main Function Area

$Script:ie = New-Object -ComObject InternetExplorer.Application
login-atctsomatic -Browser $ie
DownloadReport-AtctsOmatic @ReportVars
$ie.document.close()
$ie.quit()
return

#endregion
