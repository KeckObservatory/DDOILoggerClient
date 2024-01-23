import { useState, useEffect } from 'react'
import MUIDataTable, { MUIDataTableOptions } from "mui-datatables"
import { Control } from './control'
import { styled } from '@mui/material/styles'
import Stack from '@mui/material/Stack'

export interface Props {

}

export interface Log {
    "_id"?: string | { "$oid": string },
    "loggername": string,
	"utc_sent": string,
    "utc_received": string | { "$date": string },
	"hostname": string,
	"level": string,
	"subsystem": string,
	"author": null | string,
	"semid": null | string,
	"progid": null | string,
	"message": string 
}

const DataTableContainer = styled('div')(() => ({
    '& .MuiTableCell-root': {
        '&:nth-of-type(0)': {
            width: '250px',
            paddingLeft: '1rem',
        },
        '&:nth-of-type(1)': {
            width: '70px',
            paddingLeft: '1rem',
        },
        '&:nth-of-type(2)': {
            width: '70px',
            paddingLeft: '1rem',
        },
        '&:nth-of-type(3)': {
            width: '70px',
            paddingLeft: '1rem',
        },
        '&:nth-last-of-type(1)': {
            width: '1350px',
            paddingLeft: '1rem',
        },
    },
}));


export const LogView = () => {

    const [logs, setLogs] = useState([] as Log[])

    useEffect(() => {
    }, [])

    const options: MUIDataTableOptions = {
        filterType: 'dropdown',
        selectableRowsHeader: false,
        selectableRowsHideCheckboxes: false,
        selectableRows: 'none',
        rowsPerPage: 25,
        setRowProps: () => {
            return {
                style: { padding: '0px' },
            };
        },
        setTableProps: () => {
            return {
                padding: 'none',
            };
        },
    }

    const columns = [
        { name: '_id', label: 'Log ID', options: { display: false } },
        { name: 'utc_sent', label: 'Datetime Sent', options: { display: false } },
        { name: 'utc_received', label: 'Datetime' },
        { name: 'hostname', label: 'Hostname', options: { display: false } },
        { name: 'level', label: 'Level', options: { display: false } },
        { name: 'subsystem', label: 'Subsystem' },
        { name: 'author', label: 'Author', options: { display: false } },
        { name: 'semid', label: 'Semid' },
        { name: 'progid', label: 'ProgID', options: { display: false } },
        { name: 'message', label: 'Message', 
          options: { 
            filter: false,
            display: true,
            customBodyRender: (value: string) => {
                return (value.split('\n').map((str: string) => {return <div style={{padding: "0px"}}>{str}</div>}))
            }
         } },
    ]

    return (
        <Stack sx={{paddingTop: '16px', height: '100%'}}>
            <Control setLogs={setLogs} />
            <DataTableContainer>
                <MUIDataTable
                    data={logs}
                    columns={columns}
                    options={options}
                    title={""}
                />
            </DataTableContainer>
        </Stack>
    )

}