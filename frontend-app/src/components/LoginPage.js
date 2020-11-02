import React, {Component} from "react";
import NavBar from "./NavBar";
import HomePageSideBar from "./HomePageSideBar";
import { DetailsList, DetailsListLayoutMode, Selection } from '@fluentui/react/lib/DetailsList';
import {

  DefaultButton,
  Link,
  MessageBar,
  MessageBarType,
  PrimaryButton,
  Stack,
  styled,
  TextField, Dialog, DialogType, DialogFooter
} from '@fluentui/react';


class LoginPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            solutions: [],
            columns: []
        };
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleSubmit(event) {
        console.log('handle submit', event)
    }

    render() {

        const modelProps = {
          isBlocking: false,
          isModeless: true,
          styles: {main: {
    selectors: {
      '@media (min-width: 0px)': {
        maxWidth: 400,
        width: 400
      }
    }
  } },
        };
        const dialogContentProps = {
          type: DialogType.normal,
          title: 'Log in',
        };

        return (
        <React.Fragment>
            <div className="nav-bar">
                <img className="nav-bar-logo" src="/static/frontend-app/lone-star-logo.png"/>
            </div>
            <Dialog hidden={false} dialogContentProps={dialogContentProps} modalProps={modelProps}>

            <form onSubmit={this.handleSubmit()}>
              <Stack
                tokens={{
                  childrenGap: '1em',
                }}>

                <TextField label="Email" required/>
                <TextField label="Password" required type="password" canRevealPassword />
                <Link>Forgot password</Link>
              </Stack>
              <DialogFooter>
                  <PrimaryButton onClick={this.handleSubmit} text="Login" className="width-450" />

                </DialogFooter>
            </form>
    </Dialog>
        </React.Fragment>
        );
    }
}

export default LoginPage;